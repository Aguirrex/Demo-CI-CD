from pydantic import BaseModel
from typing import Optional

class PetBase(BaseModel):
    name: str
    species: str
    breed: Optional[str] = None
    age: Optional[int] = None
    owner_id: Optional[int] = None

class PetCreate(PetBase):
    pass

class Pet(PetBase):
    id: int

    class Config:
        orm_mode = True