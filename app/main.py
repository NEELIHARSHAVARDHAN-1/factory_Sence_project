from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import threading

from .database import Base, engine, SessionLocal
from . import schemas, crud
from .alert_engine import process_alert
from .background import start_background_worker

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def start_worker():
    thread = threading.Thread(target=start_background_worker, daemon=True)
    thread.start()


@app.post("/telemetry")
def receive_telemetry(data: schemas.TelemetryCreate, db: Session = Depends(get_db)):
    crud.create_telemetry(db, data)
    crud.update_last_seen(db, data.device_id)

    process_alert(db, data.device_id)

    return {"status": "ok"}


@app.get("/devices/{device_id}/status", response_model=schemas.DeviceStatus)
def get_device_status(device_id: str, db: Session = Depends(get_db)):
    readings = crud.get_last_readings(db, device_id)
    state = crud.get_or_create_device_state(db, device_id)

    return {
        "device_id": device_id,
        "alert_type": state.alert_type,
        "alert_active": state.alert_active,
        "readings": readings,
    }