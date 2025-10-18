
import os

# Use SQLite by default for easy local testing.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///" + os.path.join(BASE_DIR, "app.db"))

# Simple secret key for JWT (demo only).
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-demo-key")
JWT_ALGO = "HS256"
TOKEN_EXP_MINUTES = 60
