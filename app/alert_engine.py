from sqlalchemy.orm import Session
from . import crud
from .notify import send_whatsapp
import time

# 🔥 Thresholds
TEMP_THRESHOLD = 35
VIB_THRESHOLD = 1.0

# ⏱ Prevent spam (in seconds)
COOLDOWN_SECONDS = 60


# ================================
# ALERT CHECKS
# ================================

def check_temperature_alert(readings):
    return any(r.temperature_c > TEMP_THRESHOLD for r in readings)


def check_vibration_alert(readings):
    return any(r.vibration_g > VIB_THRESHOLD for r in readings)


def determine_alert(readings):
    if check_temperature_alert(readings):
        return "TEMP"
    if check_vibration_alert(readings):
        return "VIB"
    return "NONE"


# ================================
# MAIN ALERT ENGINE
# ================================

def process_alert(db: Session, device_id: str):
    readings = crud.get_last_readings(db, device_id, limit=5)
    state = crud.get_or_create_device_state(db, device_id)

    new_alert = determine_alert(readings)

    print(f"🔍 {device_id} → {new_alert}")

    now = int(time.time())

    # ⛔ Cooldown (prevent spam)
    if state.last_alert_ts and (now - state.last_alert_ts < COOLDOWN_SECONDS):
        print("⏱ Cooldown active — skipping")
        return

    # 🚨 Send only when alert state changes
    if new_alert != state.alert_type:

        if new_alert != "NONE":
            msg = f"🚨 ALERT: {device_id} → {new_alert}"
        else:
            msg = f"✅ RESOLVED: {device_id}"

        print(msg)
        send_whatsapp(msg)

        # update state
        state.alert_type = new_alert
        state.alert_active = new_alert != "NONE"
        state.last_alert_ts = now

        db.commit()
