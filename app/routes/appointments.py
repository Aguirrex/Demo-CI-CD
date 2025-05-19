from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models import Appointment as AppointmentModel
from app.schemas import Appointment as AppointmentSchema, AppointmentCreate

router = APIRouter()


@router.post("/", response_model=AppointmentSchema)
def create_appointment(
    appointment: AppointmentCreate, db: Session = Depends(get_db)
) -> AppointmentSchema:
    db_appointment = AppointmentModel(**appointment.model_dump())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


@router.get("/{appointment_id}", response_model=AppointmentSchema)
def read_appointment(
    appointment_id: int, db: Session = Depends(get_db)
) -> AppointmentSchema:
    db_appointment = (
        db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
    )
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment


@router.get("/", response_model=List[AppointmentSchema])
def read_appointments(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[AppointmentSchema]:
    appointments_db = db.query(AppointmentModel).offset(skip).limit(limit).all()
    return [
        AppointmentSchema.model_validate(appointment) for appointment in appointments_db
    ]
