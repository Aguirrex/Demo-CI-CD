from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models import Pet as PetModel
from app.schemas import Pet as PetSchema, PetCreate

router = APIRouter()


@router.post("/", response_model=PetSchema)
def create_pet(pet: PetCreate, db: Session = Depends(get_db)) -> PetSchema:
    db_pet = PetModel(**pet.model_dump())
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet


@router.get("/{pet_id}", response_model=PetSchema)
def read_pet(pet_id: int, db: Session = Depends(get_db)) -> PetSchema:
    db_pet = db.query(PetModel).filter(PetModel.id == pet_id).first()
    if db_pet is None:
        raise HTTPException(status_code=404, detail="Pet not found")
    return db_pet


@router.get("/", response_model=List[PetSchema])
def read_pets(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[PetSchema]:
    pets_db = db.query(PetModel).offset(skip).limit(limit).all()
    return [PetSchema.model_validate(pet) for pet in pets_db]
