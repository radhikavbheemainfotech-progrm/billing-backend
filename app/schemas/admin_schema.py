from datetime import datetime
from typing import Optional,Literal
from pydantic import BaseModel,EmailStr



class UserCreateByAdmin(BaseModel):
    name: str
    email : EmailStr
    password: str
    role : Literal["staff","accountant"]
    phone: Optional[str] = None
    

class UserUpdate(BaseModel):
    name : Optional[str] = None
    email : Optional[str] = None
    password: Optional[str] = None
    role : Optional[Literal["staff","accountant"]] = None
    phone :  Optional[str] = None
    is_active :  Optional[bool] = None


class UserOut(BaseModel):
    id:int
    name: str
    email:str
    role: str
    is_active : bool

    class Config:
        from_attributes = True

