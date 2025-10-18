import os, csv, random
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Crime, Suspect, Victim, Evidence
from config import DATABASE_URL

# Cities/states lists for synthetic data
CITIES = [
    ("Mumbai", "Maharashtra"), ("Delhi", "Delhi"), ("Bengaluru", "Karnataka"),
    ("Hyderabad", "Telangana"), ("Chennai", "Tamil Nadu"), ("Pune", "Maharashtra"),
    ("Kolkata", "West Bengal"), ("Ahmedabad", "Gujarat"), ("Jaipur", "Rajasthan"),
    ("Lucknow", "Uttar Pradesh")
]
TYPES = ["Phishing", "Hacking", "Fraud", "Identity Theft", "Ransomware", "DDoS", "Malware"]
EVID_TYPES = ["Log File", "Email Header", "IP Trace", "Bank Statement", "Screenshot"]

def random_ip():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))

def generate_crimes(n=1000, months_back=12):
    base = date.today().replace(day=1)
    data = []
    for i in range(n):
        # random date in last N months
        month_offset = random.randint(0, months_back - 1)
        start = (base - timedelta(days=30*month_offset))
        d = start + timedelta(days=random.randint(0, 27))
        city, state = random.choice(CITIES)
        typ = random.choice(TYPES)
        sev = random.randint(1, 5)
        desc = f"{typ} case reported in {city}."
        ip = random_ip()
        data.append({
            "type": typ, "date": d.isoformat(), "city": city, "state": state,
            "severity": sev, "description": desc, "ip_address": ip
        })
    return data

def load_to_db(crimes, seed_people=200):
    engine = create_engine(DATABASE_URL, future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    with SessionLocal() as s:
        # Insert crimes
        for c in crimes:
            s.add(Crime(
                type=c["type"],
                date=datetime.fromisoformat(c["date"]).date(),
                city=c["city"], state=c["state"],
                severity=c["severity"], description=c["description"],
                ip_address=c["ip_address"]
            ))
        # Seed suspects & victims
        for i in range(seed_people):
            s.add(Suspect(name=f"Suspect {i+1}", age=random.randint(18,60), gender=random.choice(["M","F"]),
                          address="Unknown", criminal_history=random.choice([None, "Prior Fraud", "Prior Hacking"])))
            s.add(Victim(name=f"Victim {i+1}", age=random.randint(18,60), gender=random.choice(["M","F"]),
                         address="Unknown"))
        s.commit()
    return True

def main():
    crimes = generate_crimes(n=1200, months_back=14)
    ok = load_to_db(crimes)
    print("Loaded crimes:", len(crimes), "Status:", ok)

if __name__ == "__main__":
    main()
