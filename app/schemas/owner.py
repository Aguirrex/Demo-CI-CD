from pydantic import BaseModel
from typing import Optional, List
from .pet import Pet

class OwnerBase(BaseModel):
    full_name: str
    email: str
    phone_number: Optional[str] = None

class OwnerCreate(OwnerBase):
    pass

class Owner(OwnerBase):
    id: int
    pets: List[Pet] = []

    class Config:
        orm_mode = True