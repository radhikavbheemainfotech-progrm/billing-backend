from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.database.models import User
from app.dependencies.auth_dependency import get_current_user
import os, uuid, shutil


router = APIRouter()


UPLOAD_DIR = "static/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail = "Admin access required")
    return current_user

@router.post("/")
def upload_image(
    file : UploadFile = File(...),
    _: User = Depends(require_admin),

):
    allowed =  ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed:
       raise HTTPException(status_code=400, detail="Only JPG,PNG,WEBP allowed")

    ext = file.filename.split(".")[-1] 
    filename = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path,"wb") as f:
        shutil.copyfileobj(file.file,f)
    
    return {"url":f"http://127.0.0.1:8000/static/images/{filename}"}
