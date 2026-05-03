from datetime import datetime
from sqlalchemy.orm import Session
from . import crud
from .notify import send_whatsapp


# 🔥 TEST THRESHOLDS
TEMP_THRESHOLD = 35
VIB_THRESHOLD = 1.0

# 🔥 COOLDOWN (prevents spam)
COOLDOWN_SECONDS = 60


def check_temperature_alert(readings):
    if len(readings) < 3:
        return False
    return all(r.temperature_c > TEMP_THRESHOLD for r in readings[:3])


def check_vibration_alert(readings):
    if len(readings) < 3:
        return False
    return all(r.vibration_g > VIB_THRESHOLD for r in readings[:3])


def determine_alert(readings):
    if check_temperature_alert(readings):
        return "TEMP"
    if check_vibration_alert(readings):
        return "VIB"
    return "NONE"


def process_alert(db: Session, device_id: str):
    readings = crud.get_last_readings(db, device_id, limit=5)
    state = crud.get_or_create_device_state(db, device_id)

    new_alert = determine_alert(readings)

    print(f"🔍 Checking {device_id} → {new_alert}")

    now = datetime.utcnow()

    # ⛔ cooldown check
    if state.last_alert_ts:
        diff = (now - state.last_alert_ts).total_seconds()
        if diff < COOLDOWN_SECONDS:
            print("⏳ Cooldown active, skipping...")
            return

    if new_alert != state.alert_type:
        if new_alert != "NONE":
            msg = f"🚨 ALERT: {device_id} → {new_alert}"
        else:
            msg = f"✅ RESOLVED: {device_id}"

        print(msg)

        try:
            send_whatsapp(msg)
            state.last_alert_ts = now
        except Exception as e:
            print("❌ WhatsApp failed:", e)

        state.alert_type = new_alert
        state.alert_active = new_alert != "NONE"

        db.commit()
