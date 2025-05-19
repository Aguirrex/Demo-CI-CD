from pydantic import BaseModel, ConfigDict
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
    model_config = ConfigDict(from_attributes=True)
    id: int