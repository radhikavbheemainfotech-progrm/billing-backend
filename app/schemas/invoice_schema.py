from datetime import datetime
from typing import Optional


from pydantic import BaseModel



# class InvoiceCreate(BaseModel):
#     order_id: int
#     due_date : Optional[datetime]= None


class InvoiceOut(BaseModel):
    id : int
    order_id : int
    invoice_number : str
    amount : float
    status : str
    issued_at : datetime
    due_date : Optional[datetime]
    paid_at : Optional[datetime]

    class Config:
        from_attributes = True


# class InvoiceStatusUpdate(BaseModel):
#     status : InvoiceStatusEnum
    