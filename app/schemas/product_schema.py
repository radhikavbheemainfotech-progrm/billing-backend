from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.category_schema import CategoryOut


class ProductCreate(BaseModel):
    name :str
    price: float
    stock : int = 0
    description : Optional[str] = None
    category_id : Optional[int] = None
    image: Optional[str] = None


class ProductUpdate(BaseModel):
    name : Optional[str] = None
    price: Optional[float] = None
    stock : Optional[int] = None
    description : Optional[str] = None
    category_id : Optional[int] = None
    is_active: Optional[bool] = None   
    image: Optional[str] = None         


class ProductOut(BaseModel):
    id: int
    name : str
    price : float
    stock : int
    description : Optional[str]
    category_id : Optional[int]
    is_active: bool 
    image: Optional[str] = None 

    class Config:
        from_attributes = True
        