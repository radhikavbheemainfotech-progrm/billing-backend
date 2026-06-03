from typing import List
from fastapi import APIRouter,Depends, HTTPException,status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import User
from app.schemas.admin_schema import UserCreateByAdmin, UserUpdate, UserOut
from app.dependencies.role_dependency import require_role
from app.dependencies.auth_dependency import get_current_user
from app.core.security import hash_password




router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role.lower() != "admin":
        raise HTTPException(status_code=403,detail="Admin access required")
    return current_user
    


@router.post("/users",response_model=UserOut,status_code= status.HTTP_201_CREATED)
def create_user(
    payload: UserCreateByAdmin,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        name = payload.name,
        email = payload.email,
        hashed_password = hash_password(payload.password),
        role = payload.role,
        is_active = True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/users",response_model=List[UserOut])
def get_users(

    db:Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    users = db.query(User).filter(
        User.role.in_(["staff","accountant"])
    ).all()
    return users



@router.get("/users/{user_id}",response_model=UserOut)
def get_user(
    user_id: int,
    db:Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user



@router.put("/users/{user_id}",response_model=UserOut)
def update_user(
    user_id : int,
    payload: UserUpdate,
    db:Session = Depends(get_db),
    _: User = Depends(require_admin),

):
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role.lower() == "admin":
        raise HTTPException(status_code=403, detail = "Cannot modify another admin")
    
    update_data = payload.model_dump(exclude_unset= True)

    for field, value in update_data.items():
        if field == "password":
            user.hashed_password = hash_password(value)
        else:
            setattr(user,field,value)


    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}",status_code=status.HTTP_200_OK)
def deactive_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail = "USer not found")
    
    if user.role.lower() == "admin":
        raise HTTPException(status_code=403, detail="Cannot delete an admin")
    
    
    user.is_active = False

    db.commit()
    return {"message": f"User {user.name} deactivated successfully"}
 
    

    