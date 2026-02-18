from sqlalchemy import Column, DateTime, Integer, Float, String, ForeignKey
from db import Base
from datetime import datetime, timezone

class DeviceLogs(Base):
    __tablename__ = "devicelogs"

    id = Column(Integer, primary_key=True, index= True)
    device_id = Column(String(50))
    topic = Column(String(255))

    temperature = Column(Float)
    humidity = Column(Float)
    pressure= Column(Float)
    voltage = Column(Float)
    current = Column(Float)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Alerts(Base):
    __tablename__ = "alertlogs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50))
    topic = Column(String(255))
    alert = Column(String(255))
    actual_value = Column(Float)
    threshold = Column(Float)
    severity = Column(String(50), default="Critical")
    is_resolved = Column(Integer, default=0)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))