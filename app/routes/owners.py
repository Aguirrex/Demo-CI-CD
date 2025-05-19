from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app import models, schemas

router = APIRouter()

@router.post("/", response_model=schemas.Owner)
def create_owner(owner: schemas.OwnerCreate, db: Session = Depends(get_db)):
    db_owner = models.Owner(**owner.model_dump())
    db.add(db_owner)
    db.commit()
    db.refresh(db_owner)
    return db_owner

@router.get("/{owner_id}", response_model=schemas.Owner)
def read_owner(owner_id: int, db: Session = Depends(get_db)):
    db_owner = db.query(models.Owner).filter(models.Owner.id == owner_id).first()
    if db_owner is None:
        raise HTTPException(status_code=404, detail="Owner not found")
    return db_owner

@router.get("/", response_model=List[schemas.Owner])
def read_owners(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    owners = db.query(models.Owner).offset(skip).limit(limit).all()
    return owners