from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, create_refresh_token, hash_token, verify_password
from app.database.db import get_db
from app.database.models import User, UserRefreshToken
from datetime import datetime, timedelta
from fastapi import Request
from app.core.security import decode_token


 
router = APIRouter()


ADMIN_ROLES = {"admin"}
STAFF_ROLES = {"staff", "accountant"}
ALL_ROLES   = ADMIN_ROLES | STAFF_ROLES



@router.post("/admin-login")
def admin_login(response: Response,
          form_data: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):

    user = db.query(User).filter(
        User.email == form_data.username
        ).first()
    

    if not user or not verify_password(form_data.password,user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    
    if  user.role.strip().lower() not in ADMIN_ROLES:
        raise HTTPException(status_code=403,detail="Admin access only")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    
    access_token = create_access_token({"sub":str(user.id),"role":user.role})

    refresh_token = create_refresh_token({"sub":str(user.id),"role":user.role})

    
    db.query(UserRefreshToken).filter(UserRefreshToken.user_id == user.id).delete()

    db.add(UserRefreshToken(user_id = user.id,
                            token = hash_token(refresh_token),
                            expires_at = datetime.utcnow()+timedelta(days=7)
      ))
    
    db.commit()

    response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,
    samesite="lax",
    max_age=1800        # 30 minutes
)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age= 604800, # 7 din
    )

    return {
        "message": "Login successful",
         "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        }
        
    }


@router.get("/admin/me")
def admin_me(request: Request):

    access_token = request.cookies.get(
        "access_token"
    )

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    payload = decode_token(
        access_token,
        token_type="access"
    )

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid token",
        )
    
    role = payload.get("role")

    if not role or role.strip().lower()  not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Access denied",
                            )
    
    return {
        "user_id": payload.get("sub"),
        "role": role,
    }



@router.post("/staff-login")
def staff_login(
    response : Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    
):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if user.role.strip().lower() not in STAFF_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Staff access only")
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")


    access_token  = create_access_token({"sub": str(user.id), "role": user.role})

    refresh_token = create_refresh_token({"sub": str(user.id), "role": user.role})

    db.query(UserRefreshToken).filter(UserRefreshToken.user_id == user.id).delete()
    db.add(UserRefreshToken(user_id = user.id,token = hash_token(refresh_token),
                            expires_at = datetime.utcnow()+ timedelta(days = 7)))
    db.commit()

    response.set_cookie(key = "access_token",value = access_token,httponly=True,samesite="lax", max_age=1800)

    response.set_cookie(key="refresh_token", 
                        value=refresh_token,
                          httponly=True, 
                          samesite="lax",
                          max_age=604800)

    return {
        "message" : "Login successful",
        "user": {"id": user.id,
                  "name": user.name, 
                  "email": user.email,
                    "role": user.role},
    }

@router.get("/staff/me")
def staff_me(request: Request):

    access_token = request.cookies.get("access_token")

    if not access_token:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,detail = "not authenticated",
        )
    
    payload = decode_token(access_token, token_type="access")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,detail = "Invalid token",
        )
    
    role = payload.get("role")

    if not role or role.strip().lower() not in STAFF_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,detail="Access denied",
        )
    
    return {
        "user_id": payload.get("sub"),
        "role": role,
    }

@router.post("/logout")
def logout(
    request : Request,
    response : Response,
    db : Session = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token"
                                        )
    
    if refresh_token:

        token_data = decode_token(refresh_token,token_type="refresh")

        if token_data:

            user_id = token_data.get("sub")
            role = token_data.get("role")

            if role == "customer":
                db.query(UserRefreshToken).filter(
                UserRefreshToken.user_id == int(user_id)
            ).delete()
                
            else:

                db.query(UserRefreshToken).filter(
                    UserRefreshToken.user_id == int(user_id)
                ).delete()


            db.commit()

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return {"message": "Logged out successfully"}
