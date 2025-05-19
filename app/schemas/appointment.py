from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class AppointmentBase(BaseModel):
    pet_id: int
    appointment_date: datetime
    reason: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int