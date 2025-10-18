
import os, sqlite3, subprocess, sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ETL = BASE / "etl" / "load_demo_data.py"
ML = BASE / "ml" / "train_hotspot.py"
DB = BASE / "app.db"

def run_py(path, *args):
    cmd = [sys.executable, str(path), *args]
    return subprocess.run(cmd, capture_output=True, text=True, check=True)

def main():
    # 1) ETL load
    out1 = run_py(ETL)
    print("ETL Output:\n", out1.stdout)
    assert DB.exists(), "Database not created!"
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT count(*) FROM crimes")
    n_crimes = cur.fetchone()[0]
    print("Crimes loaded:", n_crimes)
    assert n_crimes >= 1000, "Insufficient crimes loaded"

    # 2) Train model
    out2 = run_py(ML, "train")
    print("ML Train Output:\n", out2.stdout)
    model_path = BASE / "ml" / "model.pkl"
    assert model_path.exists(), "Model not saved!"

    # 3) Forecast
    out3 = run_py(ML, "forecast")
    print("Forecast Output:\n", out3.stdout)

    # 4) Verify forecasts inserted
    cur.execute("SELECT count(*) FROM forecasts")
    n_fc = cur.fetchone()[0]
    con.close()
    print("Forecast rows:", n_fc)
    assert n_fc > 0, "No forecasts inserted!"

    print("\nALL TESTS PASSED ✅")

if __name__ == "__main__":
    main()
