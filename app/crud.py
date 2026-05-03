from sqlalchemy.orm import Session
from . import models
from datetime import datetime

def create_telemetry(db: Session, data):
    telemetry = models.Telemetry(
        device_id=data.device_id,
        timestamp=data.timestamp,
        temperature_c=data.temperature_c,
        vibration_g=data.vibration_g,
    )
    db.add(telemetry)
    db.commit()
    db.refresh(telemetry)
    return telemetry


def get_last_readings(db: Session, device_id: str, limit=5):
    return (
        db.query(models.Telemetry)
        .filter(models.Telemetry.device_id == device_id)
        .order_by(models.Telemetry.timestamp.desc())
        .limit(limit)
        .all()
    )


def get_or_create_device_state(db: Session, device_id: str):
    state = db.query(models.DeviceState).filter_by(device_id=device_id).first()

    if not state:
        state = models.DeviceState(
            device_id=device_id,
            last_seen=datetime.utcnow(),
            alert_type="NONE",
            alert_active=False,
        )
        db.add(state)
        db.commit()
        db.refresh(state)

    return state


def update_last_seen(db: Session, device_id: str):
    state = get_or_create_device_state(db, device_id)
    state.last_seen = datetime.utcnow()
    db.commit()
