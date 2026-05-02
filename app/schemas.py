from pydantic import BaseModel
from datetime import datetime
from typing import List

class TelemetryCreate(BaseModel):
    device_id: str
    timestamp: datetime
    temperature_c: float
    vibration_g: float


class TelemetryResponse(BaseModel):
    device_id: str
    timestamp: datetime
    temperature_c: float
    vibration_g: float

    class Config:
        from_attributes = True


class DeviceStatus(BaseModel):
    device_id: str
    alert_type: str
    alert_active: bool
    readings: List[TelemetryResponse]