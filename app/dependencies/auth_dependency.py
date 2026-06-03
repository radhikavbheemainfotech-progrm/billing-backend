from fastapi import Depends,HTTPException,status,Request
from sqlalchemy.orm import Session
from app.core.security import decode_token
from app.database.db import get_db
from app.database.models import User,Customer


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def get_current_customer(
        request: Request,
        db: Session = Depends(get_db),

) -> Customer:
    
    token = request.cookies.get("customer_access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    
    customer_id = payload.get("sub")
    customer = db.query(Customer).filter(Customer.id == int(customer_id)).first()
    if not customer or not customer.is_active:
        raise HTTPException(status_code=401, detail="Customer not found")

    return customer