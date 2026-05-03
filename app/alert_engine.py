from sqlalchemy.orm import Session
from . import crud
from .notify import send_whatsapp

# 🔥 THRESHOLDS (as per requirement)
TEMP_THRESHOLD = 75
VIB_THRESHOLD = 2.5


# ✅ TEMP: 3 consecutive readings > 75°C
def check_temperature_alert(readings):
    if len(readings) < 3:
        return False
    return all(r.temperature_c > TEMP_THRESHOLD for r in readings[:3])


# ✅ VIB: 5 consecutive readings > 2.5g
def check_vibration_alert(readings):
    if len(readings) < 5:
        return False
    return all(r.vibration_g > VIB_THRESHOLD for r in readings[:5])


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

    print(f"🔍 {device_id} → {new_alert}")

    # 🚫 BLOCK if SILENT is active
    if state.alert_type == "SILENT":
        return

    # 🚫 NO CHANGE → DO NOTHING
    if new_alert == state.alert_type:
        return

    # 🔥 SEND ONLY WHEN STATE CHANGES
    if new_alert != "NONE":
        msg = f"🚨 ALERT: {device_id} → {new_alert}"
    else:
        msg = f"✅ RESOLVED: {device_id}"

    print("📤 Sending:", msg)
    send_whatsapp(msg)

    # ✅ UPDATE STATE
    state.alert_type = new_alert
    state.alert_active = new_alert != "NONE"

    db.commit()
