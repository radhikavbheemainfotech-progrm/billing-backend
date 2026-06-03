from fastapi import APIRouter, Depends, HTTPException, status, Response,Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, create_refresh_token, hash_token, hash_password, verify_password,decode_token
from app.database.db import get_db
from app.database.models import Customer, CustomerRefreshToken
from app.schemas.auth_schema import UserCreate, UserOut
from datetime import datetime, timedelta


router = APIRouter()



@router.post("/register",response_model=UserOut,status_code=status.HTTP_201_CREATED)

def register(payload: UserCreate, db: Session = Depends(get_db)):

    existing = db.query(Customer).filter(Customer.email == payload.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    customer = Customer(
        name=payload.name,
        email=payload.email,
        phone = payload.phone,
        hashed_password=hash_password(payload.password),
        is_active = True,
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

@router.get("/customer/me")
def customer_me(request: Request):
     
     access_token = request.cookies.get(
          "customer_access_token"
     )

     if not access_token:
          raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,detail="Not authenticated",

          )
     
     payload = decode_token(
          access_token,
          token_type="access"
     )

     if not payload:
          raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token",
          )
     
     role = payload.get("role")

     if role != "customer":
          raise HTTPException(
               status_code=status.HTTP_403_FORBIDDEN,
               detail= "Access denied",
          )
     
     return {
          "customer_id": payload.get("sub"),
          "role" : role,
     }



@router.post("/customer-login")
def customer_login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    
        customer = db.query(Customer).filter(Customer.email == form_data.username).first()

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid email or password"
            )
        
        if not verify_password(
            form_data.password,
            customer.hashed_password
        ):
            
            raise HTTPException(status_code=401,detail="Invalid email or password")
        
        access_token = create_access_token({
            "sub": str(customer.id),
            "role": "customer"
        })

        refresh_token = create_refresh_token( {
            "sub":str(customer.id),
            "role": "customer"
        })

        db.query(CustomerRefreshToken).filter(CustomerRefreshToken.customer_id == customer.id).delete()

        db.add(CustomerRefreshToken(
            customer_id = customer.id,
            token = hash_token(refresh_token),
            expire_at = datetime.utcnow() + timedelta(days=7)
            
        ))

        db.commit()

        response.set_cookie(
            key="customer_access_token",
            value=access_token,
            httponly= True,
            samesite="lax",
            max_age= 1800,
        )

        response.set_cookie(
            key="customer_refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="lax",
            max_age=604800,
        )

        return{
            "message": "Customer login successful",
            "customer":{
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
            }
        }
