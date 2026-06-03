from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional


from app.database.db import get_db
from app.database.models import Product, Category, User
from app.dependencies.role_dependency import require_role
from app.dependencies.auth_dependency import get_current_user
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductOut


router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def require_admin_or_staff(current_user: User = Depends(get_current_user)):
    if current_user.role.lower() not in ["admin","staff"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return current_user



@router.post("/",response_model=ProductOut,status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    category = db.query(Category).filter(Category.id == payload.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    

    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/",response_model=List[ProductOut])
def list_products(
    category_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_or_staff),
):
    
    query  = db.query(Product)

    if category_id is not None:
        query = query.filter(Product.category_id == category_id)

    if is_active is not None:
        query = query.filter(Product.is_active == is_active)

    return query.order_by(Product.created_at.desc()).all()


@router.get("/{product_id}",response_model=ProductOut)
def get_product(
    product_id : int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_or_staff),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product




@router.patch("/{product_id}",response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if payload.category_id:
        category = db.query(Category).filter(Category.id == payload.category_id).first()
        if not category:
            raise HTTPException(status_code=404,detail="Category not found")
        
    updated_data = payload.model_dump(exclude_unset=True)
    for field, value in updated_data.items():
        setattr(product,field,value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}",status_code=status.HTTP_200_OK)
def delete_product(
    product_id:int,
    db:Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404,detail = "Product not found")
    
    product.is_active = False
    db.commit()
    return {"message": f"Product '{product.name}' deactivated successfully"}
