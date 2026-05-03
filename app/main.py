from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import threading
import os

from .database import Base, engine, SessionLocal
from . import schemas, crud, models
from .alert_engine import process_alert
from .background import start_background_worker
from .notify import send_whatsapp

from dotenv import load_dotenv
load_dotenv()


# ✅ DB INIT (ONLY ONCE)
if os.getenv("RESET_DB") == "true":
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    print("⚠️ Database RESET DONE")
else:
    models.Base.metadata.create_all(bind=engine)


app = FastAPI()


# 🔌 DB SESSION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔥 BACKGROUND WORKER
@app.on_event("startup")
def start_worker():
    thread = threading.Thread(target=start_background_worker, daemon=True)
    thread.start()
    print("🟢 Background worker started")


# 📡 TELEMETRY
@app.post("/telemetry")
def receive_telemetry(data: schemas.TelemetryCreate, db: Session = Depends(get_db)):
    crud.create_telemetry(db, data)
    crud.update_last_seen(db, data.device_id)

    process_alert(db, data.device_id)

    return {"status": "ok"}


# 📊 STATUS
@app.get("/devices/{device_id}/status")
def get_device_status(device_id: str, db: Session = Depends(get_db)):
    readings = crud.get_last_readings(db, device_id)
    state = crud.get_or_create_device_state(db, device_id)

    return {
        "device_id": device_id,
        "alert_type": state.alert_type,
        "alert_active": state.alert_active,
        "readings": readings,
    }


# 🧪 DEBUG ENV
@app.get("/debug-env")
def debug_env():
    return {
        "sid_set": bool(os.getenv("TWILIO_ACCOUNT_SID")),
        "token_set": bool(os.getenv("TWILIO_AUTH_TOKEN")),
        "from": os.getenv("TWILIO_WHATSAPP_FROM"),
        "to": os.getenv("TWILIO_WHATSAPP_TO"),
    }


# 📲 TEST WHATSAPP
@app.get("/test-whatsapp")
def test_whatsapp():
    send_whatsapp("🚀 TEST MESSAGE FROM RAILWAY")
    return {"status": "sent"}


# 🏠 ROOT
@app.get("/")
def root():
    return {"message": "FactorySense API running 🚀"}
