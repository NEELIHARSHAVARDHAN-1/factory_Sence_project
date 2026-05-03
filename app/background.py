import time
from datetime import datetime
from sqlalchemy.orm import Session

from .database import SessionLocal
import time
from datetime import datetime
from sqlalchemy.orm import Session

from .database import SessionLocal
from . import models
from .notify import send_whatsapp

# ⏱️ Config
SILENT_THRESHOLD_SECONDS = 120   # 2 minutes
CHECK_INTERVAL = 30              # run every 30 seconds


def check_silent_devices():
    db: Session = SessionLocal()

    try:
        devices = db.query(models.DeviceState).all()
        now = datetime.utcnow()

        for device in devices:
            # skip if never seen
            if not device.last_seen:
                continue

            diff = (now - device.last_seen).total_seconds()

            # 🚨 SILENT ALERT (independent of TEMP/VIB)
            if diff > SILENT_THRESHOLD_SECONDS:
                if not device.is_silent:
                    msg = f"🚨 SILENT ALERT: {device.device_id}"
                    print(msg)

                    try:
                        send_whatsapp(msg)
                    except Exception as e:
                        print("❌ WhatsApp error:", e)

                    device.is_silent = True
                    db.commit()

            # ✅ SILENT RESOLVED
            else:
                if device.is_silent:
                    msg = f"✅ SILENT RESOLVED: {device.device_id}"
                    print(msg)

                    try:
                        send_whatsapp(msg)
                    except Exception as e:
                        print("❌ WhatsApp error:", e)

                    device.is_silent = False
                    db.commit()

    except Exception as e:
        print("❌ Background worker error:", e)

    finally:
        db.close()


def start_background_worker():
    print("🟢 Silent failure background worker started")

    while True:
        check_silent_devices()
        time.sleep(CHECK_INTERVAL)
from . import models
from .notify import send_whatsapp

SILENT_THRESHOLD_SECONDS = 120
CHECK_INTERVAL = 30


def check_silent_devices():
    db: Session = SessionLocal()

    try:
        devices = db.query(models.DeviceState).all()
        now = datetime.utcnow()

        for device in devices:
            if not device.last_seen:
                continue

            diff = (now - device.last_seen).total_seconds()

            # 🚨 SILENT ALERT
            if diff > SILENT_THRESHOLD_SECONDS:

                # Only trigger if NOT already silent
                if device.alert_type != "SILENT":
                    msg = f"🚨 SILENT ALERT: {device.device_id}"
                    print(msg)
                    send_whatsapp(msg)

                    device.alert_type = "SILENT"
                    device.alert_active = True
                    db.commit()

            # ✅ SILENT RESOLVED
            else:
                if device.alert_type == "SILENT":
                    msg = f"✅ SILENT RESOLVED: {device.device_id}"
                    print(msg)
                    send_whatsapp(msg)

                    # ⚠️ IMPORTANT: reset safely
                    device.alert_type = "NONE"
                    device.alert_active = False
                    db.commit()

    except Exception as e:
        print("❌ Background error:", e)

    finally:
        db.close()


def start_background_worker():
    print("🟢 Silent failure background worker started")

    while True:
        check_silent_devices()
        time.sleep(CHECK_INTERVAL)
