
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DATABASE_URL
from models import Base, Crime, Suspect, Victim, Evidence, Forecast
from util_jwt import jwt_decode, make_demo_token

app = Flask(__name__)

engine = create_engine(DATABASE_URL, echo=False, future=True)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def require_auth(f):
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401
        token = auth.split(" ", 1)[1]
        try:
            jwt_decode(token)
        except Exception as e:
            return jsonify({"error": str(e)}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    # Demo: accept admin/admin123 only
    if data.get("username") == "admin" and data.get("password") == "admin123":
        return {"token": make_demo_token("admin")}
    return {"error": "Invalid credentials"}, 401

# ----- CRUD for Crimes -----
@app.get("/crimes")
@require_auth
def list_crimes():
    with SessionLocal() as s:
        q = s.query(Crime).all()
        return jsonify([{
            "crime_id": c.crime_id,
            "type": c.type,
            "date": c.date.isoformat(),
            "city": c.city,
            "state": c.state,
            "severity": c.severity,
            "description": c.description,
            "ip_address": c.ip_address
        } for c in q])

@app.post("/crimes")
@require_auth
def create_crime():
    data = request.get_json() or {}
    try:
        date_obj = datetime.fromisoformat(data["date"]).date()
    except Exception:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}, 400
    c = Crime(
        type=data.get("type", "Unknown"),
        date=date_obj,
        city=data.get("city", "Unknown City"),
        state=data.get("state", "Unknown State"),
        severity=int(data.get("severity", 1)),
        description=data.get("description"),
        ip_address=data.get("ip_address")
    )
    with SessionLocal() as s:
        s.add(c)
        s.commit()
        s.refresh(c)
        return {"crime_id": c.crime_id}, 201

@app.put("/crimes/<int:crime_id>")
@require_auth
def update_crime(crime_id):
    data = request.get_json() or {}
    with SessionLocal() as s:
        c = s.get(Crime, crime_id)
        if not c:
            return {"error": "Not found"}, 404
        if "type" in data: c.type = data["type"]
        if "date" in data: c.date = datetime.fromisoformat(data["date"]).date()
        if "city" in data: c.city = data["city"]
        if "state" in data: c.state = data["state"]
        if "severity" in data: c.severity = int(data["severity"])
        if "description" in data: c.description = data["description"]
        if "ip_address" in data: c.ip_address = data["ip_address"]
        s.commit()
        return {"updated": True}

@app.delete("/crimes/<int:crime_id>")
@require_auth
def delete_crime(crime_id):
    with SessionLocal() as s:
        c = s.get(Crime, crime_id)
        if not c:
            return {"error": "Not found"}, 404
        s.delete(c)
        s.commit()
        return {"deleted": True}

# ----- Simple GET/POST for suspects -----
@app.get("/suspects")
@require_auth
def list_suspects():
    with SessionLocal() as s:
        q = s.query(Suspect).all()
        return jsonify([{
            "suspect_id": x.suspect_id,
            "name": x.name,
            "age": x.age,
            "gender": x.gender,
            "address": x.address,
            "criminal_history": x.criminal_history
        } for x in q])

@app.post("/suspects")
@require_auth
def create_suspect():
    data = request.get_json() or {}
    spt = Suspect(
        name=data.get("name", "Unknown"),
        age=data.get("age"),
        gender=data.get("gender"),
        address=data.get("address"),
        criminal_history=data.get("criminal_history")
    )
    with SessionLocal() as s:
        s.add(spt)
        s.commit()
        s.refresh(spt)
        return {"suspect_id": spt.suspect_id}, 201

# ----- Forecast endpoints -----
@app.get("/forecasts")
@require_auth
def get_forecasts():
    with SessionLocal() as s:
        q = s.query(Forecast).all()
        return jsonify([{
            "id": f.id,
            "city": f.city,
            "state": f.state,
            "month": f.month,
            "risk_score": f.risk_score,
            "label": f.label,
            "created_at": f.created_at.isoformat()
        } for f in q])

if __name__ == "__main__":
    app.run(debug=True)
