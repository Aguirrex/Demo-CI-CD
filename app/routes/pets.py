from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app import models, schemas

router = APIRouter()

@router.post("/", response_model=schemas.Pet)
def create_pet(pet: schemas.PetCreate, db: Session = Depends(get_db)):
    db_pet = models.Pet(**pet.model_dump())
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet

@router.get("/{pet_id}", response_model=schemas.Pet)
def read_pet(pet_id: int, db: Session = Depends(get_db)):
    db_pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if db_pet is None:
        raise HTTPException(status_code=404, detail="Pet not found")
    return db_pet

@router.get("/", response_model=List[schemas.Pet])
def read_pets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pets = db.query(models.Pet).offset(skip).limit(limit).all()
    return pets