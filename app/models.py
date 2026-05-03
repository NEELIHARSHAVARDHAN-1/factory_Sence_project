from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from datetime import datetime
from .database import Base


# 📡 TELEMETRY TABLE
class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    temperature_c = Column(Float)
    vibration_g = Column(Float)


# 🧠 DEVICE STATE TABLE (IMPORTANT)
class DeviceState(Base):
    __tablename__ = "device_state"

    device_id = Column(String, primary_key=True, index=True)

    # last time device sent data
    last_seen = Column(DateTime, default=datetime.utcnow)

    # current alert type: TEMP / VIB / NONE
    alert_type = Column(String, default="NONE")

    # is alert active or not
    alert_active = Column(Boolean, default=False)

    # ✅ NEW: cooldown tracking (VERY IMPORTANT)
    last_alert_ts = Column(Integer, nullable=True)
