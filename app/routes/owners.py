from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models import Owner as OwnerModel
from app.schemas import Owner as OwnerSchema, OwnerCreate

router = APIRouter()


@router.post("/", response_model=OwnerSchema)
def create_owner(owner: OwnerCreate, db: Session = Depends(get_db)) -> OwnerSchema:
    db_owner = OwnerModel(**owner.model_dump())
    db.add(db_owner)
    db.commit()
    db.refresh(db_owner)
    return db_owner


@router.get("/{owner_id}", response_model=OwnerSchema)
def read_owner(owner_id: int, db: Session = Depends(get_db)) -> OwnerSchema:
    db_owner = db.query(OwnerModel).filter(OwnerModel.id == owner_id).first()
    if db_owner is None:
        raise HTTPException(status_code=404, detail="Owner not found")
    return db_owner


@router.get("/", response_model=List[OwnerSchema])
def read_owners(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[OwnerSchema]:
    owners_db = db.query(OwnerModel).offset(skip).limit(limit).all()
    return [OwnerSchema.model_validate(owner) for owner in owners_db]
