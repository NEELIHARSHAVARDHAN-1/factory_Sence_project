from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from datetime import datetime
from .database import Base

class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    temperature_c = Column(Float)
    vibration_g = Column(Float)


class DeviceState(Base):
    __tablename__ = "device_state"

    device_id = Column(String, primary_key=True, index=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    alert_type = Column(String, default="NONE")
    alert_active = Column(Boolean, default=False)