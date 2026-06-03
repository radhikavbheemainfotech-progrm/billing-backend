from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    

class CategoryOut(BaseModel):
    id : int
    name : str
    description : Optional[str] = None
    created_at: datetime


    class Config:
        from_attributes = True