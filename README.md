# FactorySense IoT Alert System

This project implements an IoT alert pipeline using FastAPI.  
It ingests telemetry from devices, detects abnormal patterns, and sends WhatsApp alerts with proper deduplication.

---

## Features

- FastAPI backend for telemetry ingestion  
- Alert detection (TEMP, VIB, SILENT)  
- WhatsApp notifications via Twilio  
- Sensor simulator for testing  

---

## API Endpoints

- POST /telemetry  
- GET /devices/{device_id}/status  

---

## How to Run

pip install -r requirements.txt  
uvicorn app.main:app --reload  

---

## Simulator

python simulator.py  

---

## Deployment

Live API URL:  
https://factorysenceproject-production.up.railway.app/
