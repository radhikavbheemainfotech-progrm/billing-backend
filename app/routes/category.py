from typing import List

from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_db
from app.database.models import Category, User
from app.schemas.category_schema import  CategoryOut,CategoryCreate
from app.dependencies.auth_dependency import get_current_user



router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/",response_model=List[CategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return db.query(Category).order_by(Category.name).all()


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    existing = db.query(Category).filter(Category.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category