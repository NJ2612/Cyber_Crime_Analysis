
from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, Table, DateTime, Float
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Association tables for many-to-many relations
crime_suspect = Table(
    "crime_suspect", Base.metadata,
    Column("crime_id", Integer, ForeignKey("crimes.crime_id"), primary_key=True),
    Column("suspect_id", Integer, ForeignKey("suspects.suspect_id"), primary_key=True)
)

crime_victim = Table(
    "crime_victim", Base.metadata,
    Column("crime_id", Integer, ForeignKey("crimes.crime_id"), primary_key=True),
    Column("victim_id", Integer, ForeignKey("victims.victim_id"), primary_key=True)
)

class Crime(Base):
    __tablename__ = "crimes"
    crime_id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(100), nullable=False)
    date = Column(Date, nullable=False)
    city = Column(String(120), nullable=False)
    state = Column(String(120), nullable=False)
    severity = Column(Integer, nullable=False, default=1)  # 1-5
    description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6 (simplified)

    suspects = relationship("Suspect", secondary=crime_suspect, back_populates="crimes")
    victims = relationship("Victim", secondary=crime_victim, back_populates="crimes")
    evidence_items = relationship("Evidence", back_populates="crime", cascade="all, delete-orphan")

class Suspect(Base):
    __tablename__ = "suspects"
    suspect_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    criminal_history = Column(Text, nullable=True)

    crimes = relationship("Crime", secondary=crime_suspect, back_populates="suspects")

class Victim(Base):
    __tablename__ = "victims"
    victim_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)

    crimes = relationship("Crime", secondary=crime_victim, back_populates="victims")

class Evidence(Base):
    __tablename__ = "evidence"
    evidence_id = Column(Integer, primary_key=True, autoincrement=True)
    crime_id = Column(Integer, ForeignKey("crimes.crime_id"), nullable=False)
    type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(255), nullable=True)

    crime = relationship("Crime", back_populates="evidence_items")

class Forecast(Base):
    __tablename__ = "forecasts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String(120), nullable=False)
    state = Column(String(120), nullable=False)
    month = Column(String(7), nullable=False)  # YYYY-MM
    risk_score = Column(Float, nullable=False)
    label = Column(String(20), nullable=False)  # e.g., 'HIGH' / 'LOW' / 'MEDIUM'
    created_at = Column(DateTime, nullable=False)
