from sqlalchemy.orm import Session
from . import crud
from .notify import send_whatsapp

TEMP_THRESHOLD = 75
VIB_THRESHOLD = 2.5


def check_temperature_alert(readings):
    if len(readings) < 3:
        return False
    return all(r.temperature_c > TEMP_THRESHOLD for r in readings[:3])


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

    if new_alert != state.alert_type:
        if new_alert != "NONE":
            msg = f"🚨 ALERT: {device_id} → {new_alert}"
            print(msg)
            send_whatsapp(msg)
        else:
            msg = f"✅ RESOLVED: {device_id}"
            print(msg)
            send_whatsapp(msg)

        state.alert_type = new_alert
        state.alert_active = new_alert != "NONE"
        db.commit()