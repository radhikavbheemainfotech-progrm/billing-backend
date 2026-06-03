# from fastapi import APIRouter, Depends, HTTPException, status,Response,Request
# from sqlalchemy.orm import Session
# from pydantic import BaseModel
# from fastapi.security import OAuth2PasswordRequestForm

# from app.core.security import (create_access_token, hash_password,verify_password,create_refresh_token,hash_token,verify_token_hash,decode_token,)

# from app.database.db import get_db
# from app.database.models import User,Customer,UserRefreshToken,CustomerRefreshToken

# from app.schemas.auth_schema import   UserCreate, UserOut,UserToken,CustomerToken
# from datetime import datetime, timedelta
# from jose import JWTError,jwt
# from app.core.config import settings
# from typing import Union

# router = APIRouter()


# @router.post("/register",response_model=UserOut,status_code=status.HTTP_201_CREATED)

# def register(payload: UserCreate, db: Session = Depends(get_db)):

#     existing = db.query(Customer).filter(Customer.email == payload.email).first()

#     if existing:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     customer = Customer(
#         name=payload.name,
#         email=payload.email,
#         phone = payload.phone,
#         hashed_password=hash_password(payload.password),
#         is_active = True,
#     )

#     db.add(customer)
#     db.commit()
#     db.refresh(customer)
#     return customer



# @router.post("/admin-login")
# def admin_login(response: Response,
#           form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):

#     user = db.query(User).filter(
#         User.email == form_data.username
#         ).first()
    

#     if not user or not verify_password(form_data.password,user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email or password",
#         )
    
#     print("role value  :", repr(user.role))
#     print("role type   :", type(user.role))
#     print("db url      :", db.bind.url)
#     print("condition   :", user.role.strip().lower() not in ["admin", "staff", "accountant"])

#     if  user.role.strip().lower() not in ["admin","staff","accountant"
#         ]:

#         raise HTTPException(status_code=403,detail="Access denied")
    
#     access_token = create_access_token({"sub":str(user.id),"role":user.role})

#     refresh_token = create_refresh_token({"sub":str(user.id),"role":user.role})

    
#     db.query(UserRefreshToken).filter(UserRefreshToken.user_id == user.id).delete()

#     db.add(UserRefreshToken(user_id = user.id,
#                             token = hash_token(refresh_token),
#                             expires_at = datetime.utcnow()+timedelta(days=7)
#       ))
    
#     db.commit()


#     response.set_cookie(
#         key="refresh_token",
#         value=refresh_token,
#         httponly=True,
#         samesite="lax",
#         max_age= 604800, # 7 din
#     )

#     return {
#         "message": "Login successful",
#         "access_token": access_token,
#          "user": {
#             "id": user.id,
#             "name": user.name,
#             "email": user.email,
#             "role": user.role,
#         }
        
#     }


# # @router.post("/staff-login")
# # def staff_login(
# #     form_data: OAuth2PasswordRequestForm = Depends(),
# #     db: Session = Depends(get_db),
# #     response: Response = None,
# # ):
# #     user = db.query(User).filter(User.email == form_data.username).first()

# #     if not user or not verify_password(form_data.password, user.hashed_password):
# #         raise HTTPException(status_code=401, detail="Invalid credentials")
    
# #     if user.role.lower() not in ["staff", "accountant"]:
# #         raise HTTPException(status_code=403, detail="Staff access only")
    
# #     if not user.is_active:
# #         raise HTTPException(status_code=403, detail="Account is deactivated")


# #     access_token  = create_access_token({"sub": str(user.id), "role": user.role})

# #     refresh_token = create_refresh_token({"sub": str(user.id), "role": user.role})

# #     # save refresh token
# #     db_token = db.query(UserRefreshToken).filter(UserRefreshToken.user_id == user.id).first()
# #     if db_token:
# #         db_token.token = hash_token(refresh_token)
# #         db_token.expires_at = datetime.utcnow() + timedelta(days=7)
# #     else:
# #         db.add(UserRefreshToken(
# #             user_id=user.id,
# #             token=hash_token(refresh_token),
# #             expires_at=datetime.utcnow() + timedelta(days=7),
# #         ))
# #     db.commit()

# #     response.set_cookie(key="refresh_token", 
# #                         value=refresh_token,
# #                           httponly=True, 
# #                           samesite="lax",
# #                           max_age=604800)

# #     return {
# #         "access_token": access_token,
# #         "token_type": "bearer",
# #         "user": {"id": user.id,
# #                   "name": user.name, 
# #                   "email": user.email,
# #                     "role": user.role}
# #     }


# @router.post("/customer-login")
# def customer_login(
#     response: Response,
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(get_db)
# ):
    
#         customer = db.query(Customer).filter(Customer.email == form_data.username).first()

#         if not customer:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid email or password"
#             )
        
#         if not verify_password(
#             form_data.password,
#             customer.hashed_password
#         ):
            
#             raise HTTPException(status_code=401,detail="Invalid email or password")
        
#         access_token = create_access_token({
#             "sub": str(customer.id),
#             "role": "customer"
#         })

#         refresh_token = create_refresh_token( {
#             "sub":str(customer.id),
#             "role": "customer"
#         })

#         db.query(CustomerRefreshToken).filter(CustomerRefreshToken.customer_id == customer.id).delete()

#         db.add(CustomerRefreshToken(
#             customer_id = customer.id,
#             token = hash_token(refresh_token),
#             expire_at = datetime.utcnow() + timedelta(days=7)
            
#         ))

#         db.commit()

#         response.set_cookie(
#             key="access_token",
#             value=access_token,
#             httponly= True,
#             samesite="lax",
#             max_age= 1800,
#         )

#         response.set_cookie(
#             key="refresh_token",
#             value=refresh_token,
#             httponly=True,
#             samesite="lax",
#             max_age=604800,
#         )

#         return{
#             "message": "Customer login successful",
#             "customer":{
#                 "id": customer.id,
#                 "name": customer.name,
#                 "email": customer.email,
#             }
#         }

        

# class RefreshRequest(BaseModel):
#     refresh_token: str


# @router.post("/refresh",response_model=Union[UserToken,CustomerToken])

# def refresh(request: Request,
#             response: Response, 
#             db: Session = Depends(get_db)):

#     refresh_token = request.cookies.get("refresh_token")


#     if not refresh_token:
#         raise HTTPException(status_code=401,detail="Refresh token missing")
    

#     token_data = decode_token(refresh_token, token_type="refresh")

#     if not token_data:
#         raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


#     user_id = token_data.get("sub")
#     role = token_data.get("role")


#     if role == "customer":

#         customer = db.query(Customer).filter(
#             Customer.id == int(user_id)
#         ).first()

#         if not customer:
#             raise HTTPException(
#                 status_code=401,
#                 detail="Customer not found"
#             )
        
#         db_token = db.query(
#             CustomerRefreshToken
#         ).filter(
#             CustomerRefreshToken.customer_id == customer.id
#         ).first()



#  # User/Admin/Staff/Accountant

#     else:
#         user = db.query(User).filter(
#             User.id == int(user_id)
#         ).first()

#         if not user:
#             raise HTTPException(
#                 status_code=401,
#                 detail="User not found"
#             )
        
#         db_token = db.query(
#             UserRefreshToken
#         ).filter(
#             UserRefreshToken.user_id == user.id
#         ).first()
    
#     if not db_token:
#         raise HTTPException(status_code=401,
#                             detail="Token not found")
    
#     if not verify_token_hash(
#         refresh_token,db_token.token
#     ):
#         raise HTTPException(status_code=401,detail="Token mismatch")
    
#     new_access_token = create_access_token({
#         "sub": str(user_id),
#         "role": role
#     })

#     new_refresh_token = create_refresh_token({
#         "sub": str(user_id),
#         "role": role
#     })

#     db_token.token = hash_token(new_refresh_token)
#     db_token.expire_at = datetime.utcnow() + timedelta(days=7)

#     db.commit()

#     response.set_cookie(
#         key="access_token",
#         value=new_access_token,
#         httponly=True,
#         samesite="lax",
#         max_age=1800
#     )

#     response.set_cookie(
#         key="refresh_token",
#         value=new_refresh_token,
#         httponly=True,
#         samesite="lax",
#         max_age=604800
#     )

#     if role == "customer":
#         return {
#         "access_token": new_access_token,
#         "refresh_token": new_refresh_token,
#         "token_type": "bearer",
#         "customer_id": customer.id
#     }

#     return{
#         "access_token": new_access_token,
#         "refresh_token":new_refresh_token,
#         "token_type": "bearer"

#     }



# @router.post("/logout")
# def logout(
#     request : Request,
#     response : Response,
#     db : Session = Depends(get_db),
# ):
#     refresh_token = request.cookies.get("refresh_token"
#                                         )
    
#     if refresh_token:

#         token_data = decode_token(refresh_token,token_type="refresh")

#         if token_data:

#             user_id = token_data.get("sub")
#             role = token_data.get("role")

#             if role == "customer":
#                 db.query(CustomerRefreshToken).filter(
#                 CustomerRefreshToken.user_id == int(user_id)
#             ).delete()
                
#             else:

#                 db.query(UserRefreshToken).filter(
#                     UserRefreshToken.user_id == int(user_id)
#                 ).delete()


#             db.commit()

#         response.delete_cookie("access_token")
#         response.delete_cookie("refresh_token")

#         return {"message": "Logged out successfully"}
