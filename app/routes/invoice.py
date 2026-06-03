# from datetime import datetime
# from typing import List

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
 
# from app.database.db import get_db
# from app.database.models import Invoice, InvoiceStatusEnum, Order, RoleEnum, User
# from app.schemas.invoice_schema import InvoiceCreate, InvoiceOut, InvoiceStatusUpdate
# from app.dependencies.auth_dependency import get_current_user
# from app.dependencies.role_dependency import require_role

# router = APIRouter()
 
# staff_or_admin = require_role(RoleEnum.staff,RoleEnum.admin)
# admin_only = require_role(RoleEnum.admin)
# accountant_or_admin = require_role(RoleEnum.accountant,RoleEnum.admin)

# def get_invoice_or_404(invoice_id: int, db: Session) -> Invoice:
#     invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
#     if not invoice:
#         raise HTTPException(status_code=404, detail="Invoice not found")
#     return invoice

# def generate_invoice_number(db:Session) -> str:
#     count = db.query(Invoice).count()
#     year = datetime.now().year
#     return f"INV-{year}-{str(count + 1).zfill(3)}"


# @router.post("",response_model=InvoiceOut,status_code=201)
# def create_invoice(
#     payload: InvoiceCreate,
#     db: Session = Depends(get_db),
#     _: User = Depends(staff_or_admin),
# ):
#     order = db.query(Order).filter(Order.id == payload.order_id).first()
#     if not order:
#         raise HTTPException(status_code=404, detail="Order not found")
    

#     existing = db.query(Invoice).filter(Invoice.order_id == payload.order_id).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="Invoice is already existed!")
    
#     if order.total_amount <= 0:
#         raise HTTPException(status_code=400, detail="Order has no items to invoice")

#     invoice = Invoice(
#         order_id = order.id,
#         invoice_number = generate_invoice_number(db),
#         amount = order.total_amount,
#         status = InvoiceStatuseEnum.unpaid,
#         due_date = payload.due_date,
#     )
#     db.add(invoice)
#     db.commit()
#     db.refresh(invoice)
#     return invoice



# @router.get("", response_model=List[InvoiceOut])
# def list_invoices(
#     db: Session = Depends(get_db),
#     _: User = Depends(accountant_or_admin),
# ):
#     return db.query(Invoice).all()


# @router.get("/{invoice_id}", response_model=InvoiceOut)
# def get_invoice(
#     invoice_id: int,
#     db: Session = Depends(get_db),
#     _: User = Depends(accountant_or_admin),
# ):
#     return get_invoice_or_404(invoice_id, db)


# @router.patch("/{invoice_id}/status", response_model=InvoiceOut)
# def update_invoice_status(
#     invoice_id: int,
#     payload: InvoiceStatusUpdate,
#     db: Session = Depends(get_db),
#     _: User = Depends(accountant_or_admin),
# ):
#     invoice = get_invoice_or_404(invoice_id, db)

#     # Paid mark karo toh paid_at timestamp save karo
#     if payload.status == InvoiceStatuseEnum.paid:
#         invoice.paid_at = datetime.utcnow()

#     if invoice.status == InvoiceStatuseEnum.paid and payload.status == InvoiceStatuseEnum.paid:
#         raise HTTPException(status_code=400,detail="Invoice is already paid")
    

#     invoice.status = payload.status
#     db.commit()
#     db.refresh(invoice)
#     return invoice


# @router.delete("/{invoice_id}", status_code=204)
# def delete_invoice(
#     invoice_id: int,
#     db: Session = Depends(get_db),
#     _: User = Depends(admin_only),
# ):
#     invoice = get_invoice_or_404(invoice_id, db)

#     if invoice.status == InvoiceStatuseEnum.paid:
#         raise HTTPException(status_code = 400, detail = "Paid invoice cannot be deleted")

#     db.delete(invoice)
#     db.commit()
