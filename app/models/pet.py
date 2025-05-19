from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Pet(Base):
    __tablename__ = "pet"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)
    breed = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    owner_id = Column(Integer, ForeignKey("owner.id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP, server_default=func.now())

    owner = relationship("Owner", back_populates="pets")
    appointments = relationship("Appointment", back_populates="pet")