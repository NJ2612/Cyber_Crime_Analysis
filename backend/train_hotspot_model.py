import os
import joblib
from datetime import timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sqlalchemy import create_engine
from config import DATABASE_URL

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

SEED = 42
os.makedirs("saved_models", exist_ok=True)
THRESHOLD_FIXED = 50         
TOP_PERCENTILE = 0.75       
TIMEWINDOW_DAYS = 90         
PAST_WINDOWS = [30, 90, 180]  

def load_crime_table():
    engine = create_engine(DATABASE_URL, future=True)
    try:
        df = pd.read_sql("SELECT * FROM crimes", engine)
    except Exception as e:
        df = pd.read_sql_table("crimes", engine)
    return df

def label_hotspots(df):
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date']).copy()
    df['city'] = df['city'].fillna('Unknown').astype(str)
    df['state'] = df['state'].fillna('Unknown').astype(str)
    city_counts = df.groupby(['city','state']).size().reset_index(name='total_count')
    df = df.merge(city_counts, on=['city','state'], how='left')
    df['is_hotspot_threshold'] = (df['total_count'] >= THRESHOLD_FIXED).astype(int)
    cutoff = city_counts['total_count'].quantile(TOP_PERCENTILE)
    city_counts['is_hotspot_top_pct'] = (city_counts['total_count'] >= cutoff).astype(int)
    df = df.drop(columns=['is_hotspot_top_pct'], errors='ignore')
    df = df.merge(city_counts[['city','state','is_hotspot_top_pct']], on=['city','state'], how='left')
    df['is_hotspot_top_pct'] = df['is_hotspot_top_pct'].fillna(0).astype(int)
    df = df.sort_values('date').reset_index(drop=True)
    df['is_hotspot_timewindow'] = 0
    grouped = df.groupby(['city','state'])['date'].apply(list).to_dict()
    def count_recent(row):
        key = (row['city'], row['state'])
        dates = grouped.get(key, [])
        cutoff_date = row['date'] - pd.Timedelta(days=TIMEWINDOW_DAYS)
        cnt = sum(1 for d in dates if (d > cutoff_date) and (d <= row['date']))
        return int(cnt)

    df['recent_count_TW'] = df.apply(count_recent, axis=1)
    df['is_hotspot_timewindow'] = (df['recent_count_TW'] >= 3).astype(int)
    df['hotspot_vote_sum'] = df['is_hotspot_threshold'] + df['is_hotspot_top_pct'] + df['is_hotspot_timewindow']
    df['is_hotspot'] = (df['hotspot_vote_sum'] >= 2).astype(int)

    return df

def add_time_window_features(df):
    df['year'] = df['date'].dt.year.fillna(0).astype(int)
    df['month'] = df['date'].dt.month.fillna(0).astype(int)
    df['day'] = df['date'].dt.day.fillna(0).astype(int)
    df['weekday'] = df['date'].dt.weekday.fillna(0).astype(int)
    df = df.sort_values('date').reset_index(drop=True)
    grouped = df.groupby(['city','state'])['date'].apply(list).to_dict()

    for w in PAST_WINDOWS:
        col = f'past_{w}d_count'
        def count_window(row, window_days=w):
            key = (row['city'], row['state'])
            dates = grouped.get(key, [])
            cutoff = row['date'] - pd.Timedelta(days=window_days)
            return sum(1 for d in dates if (d > cutoff) and (d < row['date'])) 
        df[col] = df.apply(count_window, axis=1)
        
    if 'severity' in df.columns:
        df['severity'] = pd.to_numeric(df['severity'], errors='coerce').fillna(1).astype(int)
    else:
        df['severity'] = 1
    return df
def build_preprocessor(numeric_features, categorical_features):
    numeric_transformer = Pipeline(steps=[('scaler', StandardScaler())])
    categorical_transformer = Pipeline(steps=[('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))])
    preprocessor = ColumnTransformer(transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ], remainder='drop')
    return preprocessor

def train_and_select(df):
    drop_cols = ['crime_id', 'date', 'description', 'ip_address', 'hotspot_vote_sum', 'recent_count_TW', 'total_count']
    available = [c for c in df.columns if c not in drop_cols]
    # target:
    target = 'is_hotspot'
    if target not in df.columns:
        raise ValueError("No is_hotspot label present")

    X = df.drop(columns=[c for c in drop_cols if c in df.columns] + [target], errors='ignore')
    y = df[target].astype(int)
    numeric_features = [c for c in X.columns if X[c].dtype.kind in 'biufc' and c != 'year']  # include numeric
    # include year/month/day/weekday as numeric; if you excluded year above, we can include them:
    for t in ['year','month','day','weekday']:
        if t in X.columns and t not in numeric_features:
            numeric_features.append(t)
    categorical_features = [c for c in X.columns if c not in numeric_features]

    preprocessor = build_preprocessor(numeric_features, categorical_features)
    models = {
        "RandomForest": RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=SEED),
        "DecisionTree": DecisionTreeClassifier(class_weight='balanced', random_state=SEED),
        "LinearRegression": LinearRegression()
    }
    stratify_param = y if y.nunique() > 1 else None
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=SEED, stratify=stratify_param)

    results = {}
    best_f1 = -1.0
    best_model_pipeline = None
    best_name = None

    for name, estimator in models.items():
        pipe = Pipeline(steps=[('pre', preprocessor), ('model', estimator)])
        pipe.fit(X_train, y_train)
        # predictions
        if name == "LinearRegression":
            raw_pred = pipe.predict(X_test)
            preds = (raw_pred >= 0.5).astype(int)
        else:
            preds = pipe.predict(X_test)

        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds, zero_division=0)
        rec = recall_score(y_test, preds, zero_division=0)
        f1 = f1_score(y_test, preds, zero_division=0)

        results[name] = {
            'accuracy': float(acc),
            'precision': float(prec),
            'recall': float(rec),
            'f1': float(f1)
        }

        print(f"[{name}] acc={acc:.4f}, prec={prec:.4f}, rec={rec:.4f}, f1={f1:.4f}")

        if f1 > best_f1:
            best_f1 = f1
            best_model_pipeline = pipe
            best_name = name
            best_preds = preds
            best_y_test = y_test

    # Save best model
    save_path = os.path.join("saved_models", "best_hotspot_model.joblib")
    joblib.dump({'model': best_model_pipeline, 'model_name': best_name, 'metrics': results}, save_path)
    print(f"\nBest model: {best_name} (saved to {save_path})")
    cm = confusion_matrix(best_y_test, best_preds)
    fig, ax = plt.subplots(figsize=(5,4))
    im = ax.imshow(cm, interpolation='nearest')
    ax.set_title(f"Confusion Matrix - {best_name}")
    ax.set_ylabel('True label')
    ax.set_xlabel('Predicted label')
    ax.set_xticks([0,1])
    ax.set_yticks([0,1])
    for (i, j), v in np.ndenumerate(cm):
        ax.text(j, i, int(v), ha='center', va='center')
    plt.tight_layout()
    cm_filename = os.path.join("saved_models", f"confusion_matrix_{best_name}.png")
    plt.savefig(cm_filename)
    plt.close(fig)
    print(f"Saved confusion matrix to {cm_filename}")
    
    creport = classification_report(best_y_test, best_preds, zero_division=0)
    with open(os.path.join("saved_models", f"classification_report_{best_name}.txt"), 'w') as f:
        f.write(creport)
    print(f"Saved classification report to saved_models/classification_report_{best_name}.txt")

    return results, best_name, save_path

def visualize_hotspot_city_counts(df):
    city_hotspot = df.groupby(['city','state'])['is_hotspot'].sum().reset_index(name='hotspot_count')
    top = city_hotspot.sort_values('hotspot_count', ascending=False).head(20)
    fig, ax = plt.subplots(figsize=(10,6))
    ax.barh(range(len(top)), top['hotspot_count'])
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels([f"{c}, {s}" for c,s in zip(top['city'], top['state'])])
    ax.invert_yaxis()
    ax.set_xlabel("Hotspot count (number of rows labeled hotspot)")
    ax.set_title("Top 20 city,state by hotspot count")
    plt.tight_layout()
    fname = os.path.join("saved_models", "hotspot_city_bar.png")
    plt.savefig(fname)
    plt.close(fig)
    print(f"Saved hotspot city bar chart to {fname}")
    
def main():
    print("Loading data from DB...")
    df = load_crime_table()
    print(f"Loaded {len(df)} rows from crime table")

    df = label_hotspots(df)
    df = add_time_window_features(df)

    print("\nLabel distribution (is_hotspot):")
    print(df['is_hotspot'].value_counts(normalize=False))
    visualize_hotspot_city_counts(df)

    results, best_name, best_path = train_and_select(df)

    print("\nAll model metrics:")
    for m, stats in results.items():
        print(f"{m}: {stats}")

    print(f"\nBest saved to: {best_path} (model: {best_name})")
    print("Done.")

if __name__ == "__main__":
    main()
