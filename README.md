
# Cybercrime Database & Analytics System

End-to-end demo project with:
- DB (SQLAlchemy ORM over SQLite by default; switch to PostgreSQL via `DATABASE_URL`)
- ETL data generator/loader
- Flask REST API with JWT (demo token)
- ML hotspot prediction (sklearn RandomForest with heuristic fallback)
- Streamlit dashboard
- Test runner for ETL + ML

## Quick Start (Local)

```bash
# 1) Create venv and install deps
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

# 2) Load demo data
python backend/etl/load_demo_data.py

# 3) Train model + generate forecasts
python backend/ml/train_hotspot.py train
python backend/ml/train_hotspot.py forecast

# 4) Run API (optional)
python backend/app.py

# 5) Run dashboard (optional)
streamlit run dashboard/app.py
```

### Auth (demo)
```
POST /login -> { "username":"admin", "password":"admin123" }
Authorization: Bearer <token>
```

### Switch to PostgreSQL
Set env var:
```
export DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/cybercrime
```

## Tests
```
python backend/tests/run_tests.py
```

This will: load demo data, train model (or fallback heuristic), insert forecasts, and verify row counts.
