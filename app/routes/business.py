from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import BusinessProfile,User
from app.schemas.business_schema import BusinessProfileOut,BusinessProfileUdate
from app.dependencies.auth_dependency import get_current_user



router = APIRouter()



def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user



@router.get("/",response_model=BusinessProfileOut)
def get_profile(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    profile = db.query(BusinessProfile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Business profile not set up yet")
    return profile



@router.put("/",response_model=BusinessProfileOut)
def update_profile(
    payload : BusinessProfileUdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),

):
    
    profile = db.query(BusinessProfile).first()
    if not profile:
        profile = BusinessProfile(**payload.model_dump(exclude_unset=True))
        db.add(profile)
    else:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(profile,field,value)
    

    
    db.commit()
    db.refresh(profile)
    return profile
    