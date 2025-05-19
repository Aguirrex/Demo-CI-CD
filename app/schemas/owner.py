from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from .pet import Pet


class OwnerBase(BaseModel):
    full_name: str
    email: str
    phone_number: Optional[str] = None


class OwnerCreate(OwnerBase):
    pass


class Owner(OwnerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    pets: List[Pet] = []
