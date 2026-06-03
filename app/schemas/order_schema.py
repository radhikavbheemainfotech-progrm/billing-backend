from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.invoice_schema import InvoiceOut


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class OrderCreate(BaseModel):
    customer_name:  Optional[str] = None
    customer_phone: Optional[str] = None
    items: List[OrderItemCreate]


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    product_name: Optional[str] = None

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    customer_name: str
    customer_phone: Optional[str] = None
    status: str
    total_amount: float
    created_at: datetime
    items: List[OrderItemOut] = []
    invoice: InvoiceOut | None

    class Config:
        from_attributes = True