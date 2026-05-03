import requests
import time
import random
from datetime import datetime

API_URL = "https://factorysense-api-production-14aa.up.railway.app/telemetry"


def send(device_id, temp, vib):
    payload = {
        "device_id": device_id,
        "timestamp": datetime.utcnow().isoformat(),
        "temperature_c": temp,
        "vibration_g": vib
    }

    try:
        res = requests.post(API_URL, json=payload)
        print(f"{device_id} → {res.status_code} | T={temp:.2f}, V={vib:.2f}")
    except Exception as e:
        print("ERROR:", e)


def device_normal(device_id):
    temp = random.uniform(25, 40)
    vib = random.uniform(0.5, 1.5)
    send(device_id, temp, vib)


def device_faulty(device_id, counter):
    # Cycle through scenarios
    if 10 < counter < 15:
        # TEMP ALERT
        temp = random.uniform(80, 85)
        vib = random.uniform(1.0, 1.5)

    elif 30 < counter < 40:
        # VIB ALERT
        temp = random.uniform(30, 40)
        vib = random.uniform(3.0, 3.5)

    elif 50 < counter < 70:
        # SILENT (no send)
        print(f"{device_id} → SILENT PERIOD")
        return

    else:
        temp = random.uniform(25, 40)
        vib = random.uniform(0.5, 1.5)

    send(device_id, temp, vib)


def run():
    counter = 0

    while True:
        counter += 1

        device_normal("device_1")
        device_normal("device_2")
        device_faulty("device_3", counter)

        time.sleep(10)  # spec requirement


if __name__ == "__main__":
    run()