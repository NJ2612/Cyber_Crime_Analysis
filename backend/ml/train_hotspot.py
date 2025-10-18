
import os, sys, pickle
from datetime import datetime
from collections import defaultdict
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.config import DATABASE_URL
from backend.models import Base, Crime, Forecast
import math

# Try to import sklearn; if unavailable, fallback to heuristic model
USE_SK = True
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report
except Exception as e:
    USE_SK = False

from datetime import datetime

def month_key(d):
    if isinstance(d, str):
        # Try parsing string into datetime
        try:
            d = datetime.fromisoformat(d)
        except ValueError:
            try:
                d = datetime.strptime(d, "%Y-%m-%d %H:%M:%S")
            except Exception:
                d = datetime.strptime(d, "%Y-%m-%d")
    return d.strftime("%Y-%m")

def build_features(engine):
    # Aggregate crime counts per (city,state,month) and build labels as next-month hotspot
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT city, state, date, severity FROM crimes
        """)).fetchall()
    # aggregate counts and severity sums
    monthly = defaultdict(lambda: {"count":0, "sev":0})
    dates = []
    for city, state, d, sev in rows:
        m = month_key(d)
        monthly[(city, state, m)]["count"] += 1
        monthly[(city, state, m)]["sev"] += sev
        dates.append(d)
    if not dates:
        raise RuntimeError("No data found to train")
    months = sorted({month_key(d) for d in dates})
    # build samples: for each (city,state,month) except last, label = 1 if next-month count in top quartile
    all_keys = sorted(monthly.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2]))
    # compute per-month thresholds
    per_month_counts = defaultdict(list)
    for (city,state,m),vals in monthly.items():
        per_month_counts[m].append(vals["count"])
    threshold = {m: sorted(v)[int(0.75*len(v))] if v else 0 for m,v in per_month_counts.items()}
    X, y, meta = [], [], []
    for (city, state, m), vals in all_keys:
        # next month
        y_month = next_month(m)
        if y_month not in per_month_counts:
            continue
        label = 1 if monthly.get((city,state,y_month), {"count":0})["count"] >= threshold[y_month] else 0
        # features: count, sev, rolling prev month
        prev_month = prev_month_key(m)
        prev_count = monthly.get((city,state,prev_month), {"count":0})["count"]
        prev_sev = monthly.get((city,state,prev_month), {"sev":0})["sev"]
        X.append([vals["count"], vals["sev"], prev_count, prev_sev])
        y.append(label)
        meta.append((city,state,y_month))
    return X, y, meta

def next_month(ym):
    y, m = map(int, ym.split("-"))
    m2 = m + 1
    y2 = y + (1 if m2==13 else 0)
    m2 = 1 if m2==13 else m2
    return f"{y2:04d}-{m2:02d}"

def prev_month_key(ym):
    y, m = map(int, ym.split("-"))
    m2 = m - 1
    y2 = y - (1 if m2==0 else 0)
    m2 = 12 if m2==0 else m2
    return f"{y2:04d}-{m2:02d}"

def train_and_save():
    engine = create_engine(DATABASE_URL, future=True)
    Base.metadata.create_all(engine)
    X, y, meta = build_features(engine)
    if not X:
        raise RuntimeError("Insufficient data for training")

    if USE_SK:
        # sklearn model
        import numpy as np
        X = np.array(X); y = np.array(y)
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        clf = RandomForestClassifier(n_estimators=150, random_state=42)
        clf.fit(Xtr, ytr)
        acc = clf.score(Xte, yte)
        print("RandomForest test accuracy:", round(acc, 3))
        try:
            print(classification_report(yte, clf.predict(Xte)))
        except Exception:
            pass
        model = ("sklearn_rf", clf)
    else:
        # Heuristic: risk score = weighted sum of count, sev, prev_count, prev_sev
        def predict_proba_row(row):
            c, s, pc, ps = row
            score = 0.5*c + 0.3*s + 0.15*pc + 0.05*ps
            # min-max squashing via sigmoid-ish
            prob = 1.0/(1.0 + math.exp(-0.05*(score-5)))
            return prob
        model = ("heuristic", predict_proba_row)
        print("Using heuristic model (sklearn unavailable).")

    # Save model
    out = os.path.join(os.path.dirname(__file__), "model.pkl")
    with open(out, "wb") as f:
        pickle.dump(model, f)
    print("Saved model to", out)

def generate_forecast():
    engine = create_engine(DATABASE_URL, future=True)
    Base.metadata.create_all(engine)
    # load model
    import pickle, numpy as np, math
    model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
    with open(model_path, "rb") as f:
        kind, model_obj = pickle.load(f)

    # Rebuild features for latest month only
    X, y, meta = build_features(engine)
    if not X:
        raise RuntimeError("No features available")
    # keep last N entries (meta contains city,state,next_month)
    # We'll aggregate by (city,state,next_month)
    preds = []
    if kind == "sklearn_rf":
        import numpy as np
        probs = model_obj.predict_proba(np.array(X))[:,1]
        preds = list(zip(meta, probs))
    else:
        def prob_row(row):
            c, s, pc, ps = row
            score = 0.5*c + 0.3*s + 0.15*pc + 0.05*ps
            return 1.0/(1.0 + math.exp(-0.05*(score-5)))
        preds = list(zip(meta, [prob_row(r) for r in X]))

    # Aggregate by key (city,state,month) — keep highest prob if duplicates
    best = {}
    for (city,state,ym), p in preds:
        if (city,state,ym) not in best or p > best[(city,state,ym)]:
            best[(city,state,ym)] = p

    # store into forecasts table
    from sqlalchemy.orm import sessionmaker
    from models import Forecast
    from datetime import datetime as dt
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    with SessionLocal() as s:
        for (city,state,ym), p in best.items():
            label = "HIGH" if p>=0.6 else ("MEDIUM" if p>=0.4 else "LOW")
            s.add(Forecast(city=city, state=state, month=ym, risk_score=float(p), label=label, created_at=dt.utcnow()))
        s.commit()
    print("Inserted", len(best), "forecast rows.")

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv)>1 else "train"
    if action == "train":
        train_and_save()
    elif action == "forecast":
        generate_forecast()
    else:
        print("Usage: python train_hotspot.py [train|forecast]")
