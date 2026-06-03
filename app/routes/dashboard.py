from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import Product, Category, User
from app.dependencies.auth_dependency import get_current_user



router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)):
    from fastapi import HTTPException
    if current_user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    
    total_products  = db.query(Product).filter(Product.is_active == True).count()
    low_stock       = db.query(Product).filter(Product.is_active == True, Product.stock <= 5).count()
    total_categories = db.query(Category).count()
    active_staff    = db.query(User).filter(
                        User.is_active == True,
                        User.role.in_(["staff", "accountant"])
                      ).count()

    return {
        "total_products":    total_products,
        "low_stock_items":   low_stock,
        "total_categories":  total_categories,
        "active_staff":      active_staff,
    }