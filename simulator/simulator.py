import requests
import time
import random
import logging
from datetime import datetime

# 🔗 Your deployed API
API_URL = "https://factorysenceproject-production.up.railway.app/telemetry"

HEADERS = {
    "Content-Type": "application/json"
}

# 🧾 Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    datefmt="%H:%M:%S"
)


def send(device_id, temp, vib):
    payload = {
        "device_id": device_id,
        "timestamp": datetime.utcnow().isoformat(),
        "temperature_c": temp,
        "vibration_g": vib
    }

    try:
        r = requests.post(API_URL, json=payload, headers=HEADERS)
        logging.info(f"{device_id} → {r.status_code} | T={temp:.2f}, V={vib:.2f}")
    except Exception as e:
        logging.error(f"{device_id} → ERROR: {e}")


# 🔵 DEVICE 1 → NORMAL
def device_1():
    temp = random.uniform(25, 35)   # below threshold
    vib = random.uniform(0.3, 1.5)  # below threshold
    send("device_1", temp, vib)


# 🔵 DEVICE 2 → NORMAL
def device_2():
    temp = random.uniform(28, 36)
    vib = random.uniform(0.5, 2.0)
    send("device_2", temp, vib)


# 🔴 DEVICE 3 → FULL ALERT TEST
cycle = 0


def device_3():
    global cycle
    cycle += 1

    # 🟢 NORMAL START
    if cycle < 5:
        temp = random.uniform(25, 35)
        vib = random.uniform(0.3, 1.5)

    # 🔥 TEMP ALERT (≥3 readings > 75°C)
    elif 5 <= cycle < 10:
        temp = random.uniform(80, 95)   # above threshold
        vib = random.uniform(0.5, 1.5)

    # 🟢 NORMAL (resolve TEMP)
    elif 10 <= cycle < 14:
        temp = random.uniform(25, 35)
        vib = random.uniform(0.3, 1.5)

    # 🔥 VIB ALERT (≥5 readings > 2.5g)
    elif 14 <= cycle < 22:
        temp = random.uniform(30, 40)
        vib = random.uniform(2.6, 3.5)  # above threshold

    # 🟢 NORMAL (resolve VIB)
    elif 22 <= cycle < 26:
        temp = random.uniform(25, 35)
        vib = random.uniform(0.3, 1.5)

    # 🔴 SILENT PERIOD (>2 minutes)
    elif 26 <= cycle < 40:
        logging.warning("device_3 → SILENT PERIOD")
        return

    # 🟢 RECOVERY AFTER SILENT
    else:
        temp = random.uniform(25, 35)
        vib = random.uniform(0.3, 1.5)

    send("device_3", temp, vib)

    # 🔁 Reset cycle
    if cycle > 45:
        cycle = 0


# 🔁 MAIN LOOP
while True:
    device_1()
    device_2()
    device_3()

    logging.info("-" * 50)

    time.sleep(10)
