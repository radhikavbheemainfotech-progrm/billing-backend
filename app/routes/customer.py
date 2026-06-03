from typing import List
from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.database.db import get_db
from app.database.models import Product, Customer
from app.dependencies.auth_dependency import get_current_customer
from app.schemas.product_schema import ProductOut



router = APIRouter()


@router.get("/products",response_model= List[ProductOut])

def get_products(
    db: Session = Depends(get_db),
    current_customer : Customer = Depends(get_current_customer),
):
    
    return db.query(Product).filter(
        Product.is_active == True
    ).order_by(Product.name).all()

