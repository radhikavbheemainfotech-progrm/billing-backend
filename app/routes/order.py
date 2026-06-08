from datetime import datetime, timezone
from typing import List
import io

from fastapi import APIRouter, Depends, HTTPException, status,Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from app.database.db import get_db
from app.database.models import BusinessProfile, Invoice,Order, OrderItem, Product, User,Customer
from app.dependencies.auth_dependency import get_current_customer
from app.schemas.order_schema import OrderCreate, OrderOut
from app.utils.pdf_generator import generate_invoice_pdf 
from app.core.security import decode_token



router = APIRouter()

def get_current_user_or_customer(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token") or request.cookies.get("customer_access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authentication")
    
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    role = payload.get("role")
    user_id = payload.get("sub")

    if role == "customer":
        customer = db.query(Customer).filter(Customer.id == int(user_id)).first()
        if not customer or not customer.is_active:
            raise HTTPException(status_code=401, detail="Customer not found")
        return {"role":"customer","name": customer.name,"phone":customer.phone,"id": customer.id}
    else:
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found")
        return {"role":user.role,"name":user.name,"phone":None,"id":user.id}
    



@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user_or_customer),
):
    if not payload.items:
        raise HTTPException(status_code=400, detail="At least one item is required")

    
    subtotal     = 0.0
    order_items  = []

    for item in payload.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()

        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name}",
            )

        subtotal += item.unit_price * item.quantity
        order_items.append((product, item))

    
    business = db.query(BusinessProfile).first()
    gst_rate  = getattr(business, "gst_percentage", None) or 18.0
    gst_amount   = round(subtotal * gst_rate / 100, 2)
    grand_total  = round(subtotal + gst_amount, 2) 

    if current["role"] == "customer":

        customer_name  = current["name"]
        customer_phone = current["phone"]
        billed_by_id   = None
        order_status   = "pending"
    
    else:
        customer_name  = payload.customer_name
        customer_phone = payload.customer_phone
        billed_by_id   = current["id"]
        order_status   = "completed"

    if not customer_name:
        raise HTTPException(status_code=400, detail="Customer name is required")
    

    order = Order(
        customer_name  = customer_name,
        customer_phone = customer_phone,
         customer_id    = current["id"] if current["role"] == "customer" else None,
        billed_by_id   = billed_by_id,
        total_amount   = grand_total,   
        status         = order_status,
    )

    db.add(order)
    db.flush()  

    for product, item in order_items:
        db.add(OrderItem(
            order_id   = order.id,
            product_id = item.product_id,
            quantity   = item.quantity,
            unit_price = item.unit_price,
        ))
        product.stock -= item.quantity


    if current["role"] != "customer":
        invoice_number = (
        f"INV-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{order.id:04d}"
    )
        db.add(Invoice(
        order_id       = order.id,
        invoice_number = invoice_number,
        amount         = grand_total,
        status         = "unpaid",
    ))

    db.commit()
    db.refresh(order)
    return order


@router.get("/", response_model=List[OrderOut])
def list_orders(
    db: Session = Depends(get_db),
    current : dict = Depends(get_current_user_or_customer),
):
    query = (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product),
        joinedload(Order.invoice))
    
        .order_by(Order.created_at.desc())
        
    )

    if current["role"] == "customer":
        query = query.filter(Order.customer_id == current["id"])

    return query.all()


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,                         
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user_or_customer),
):
    query = (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product),
        joinedload(Order.invoice))
        .filter(Order.id == order_id)
        
    )
    if current["role"] == "customer":
        query = query.filter(Order.customer_name == current["name"])
    
    order = query.first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order



@router.get("/{order_id}/invoice/pdf")
def download_invoice(
    order_id: int,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user_or_customer),
):
    if current["role"] == "customer":
        raise HTTPException(status_code=403, detail="Access denied. Staff generates invoices.")
    
    order = (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product),joinedload(Order.invoice))
        
        .filter(Order.id == order_id)

        .first()
    )

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    invoice  = db.query(Invoice).filter(Invoice.order_id == order_id).first()
    business = db.query(BusinessProfile).first()

    buffer = generate_invoice_pdf(order, invoice, business)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=invoice_{order.id}.pdf"},
    )