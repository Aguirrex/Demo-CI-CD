from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Appointment(Base):
    __tablename__ = "appointment"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pet.id", ondelete="CASCADE"))
    appointment_date = Column(TIMESTAMP, nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    pet = relationship("Pet", back_populates="appointments")