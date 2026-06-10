from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from typing import Union
from app.core.security import create_access_token, create_refresh_token, hash_token, verify_token_hash, decode_token
from app.database.db import get_db
from app.database.models import User, Customer, UserRefreshToken, CustomerRefreshToken
from app.schemas.auth_schema import UserToken, CustomerToken
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/refresh", response_model=Union[UserToken, CustomerToken])
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):

    role_hint = None

    
    customer_refresh = request.cookies.get("customer_refresh_token")
    admin_refresh = request.cookies.get("refresh_token")

    refresh_token = customer_refresh or admin_refresh

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    token_data = decode_token(refresh_token, token_type="refresh")

    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user_id = token_data.get("sub")
    role = token_data.get("role")

    if role == "customer":
        customer = db.query(Customer).filter(Customer.id == int(user_id)).first()

        if not customer:
            raise HTTPException(status_code=401, detail="Customer not found")

        db_token = db.query(CustomerRefreshToken).filter(
            CustomerRefreshToken.customer_id == customer.id
        ).first()

        if not db_token:
            raise HTTPException(status_code=401, detail="Token not found")

        
        if db_token.expire_at < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Refresh token expired")

    else:
        user = db.query(User).filter(User.id == int(user_id)).first()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        db_token = db.query(UserRefreshToken).filter(
            UserRefreshToken.user_id == user.id
        ).first()

        if not db_token:
            raise HTTPException(status_code=401, detail="Token not found")

    
        if db_token.expires_at < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Refresh token expired")

    if not verify_token_hash(refresh_token, db_token.token):
        raise HTTPException(status_code=401, detail="Token mismatch")

    new_access_token = create_access_token({"sub": str(user_id), "role": role})
    new_refresh_token = create_refresh_token({"sub": str(user_id), "role": role})

    db_token.token = hash_token(new_refresh_token)

    if role == "customer":
        db_token.expire_at = datetime.utcnow() + timedelta(days=7)  
    else:
        db_token.expires_at = datetime.utcnow() + timedelta(days=7)  

    db.commit()

    if role == "customer":
        response.set_cookie(key="customer_access_token", value=new_access_token,
                            httponly=True, samesite="lax", max_age=1800)
        response.set_cookie(key="customer_refresh_token", value=new_refresh_token,
                            httponly=True, samesite="lax", max_age=604800)
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "customer_id": customer.id
        }

    else:
        response.set_cookie(key="access_token", value=new_access_token,
                            httponly=True, samesite="lax", max_age=1800)
        response.set_cookie(key="refresh_token", value=new_refresh_token,
                            httponly=True, samesite="lax", max_age=604800)
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }