from pydantic import BaseModel,EmailStr,Field
from typing import Optional


# Users login

class UserCreate(BaseModel):
    name :str
    email :EmailStr
    phone : Optional[str] = None
    password : str
    
    
class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password : str
    

class UserToken(BaseModel):
    access_token : str
    refresh_token : str
    token_type : str = "bearer"
    


    # Customer login

class CustomerLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserLoginRequest(BaseModel):
    username : str
    password : str

class UserLoginOut(UserOut):

    pass

class CustomerToken(BaseModel):
    access_token : str
    refresh_token : str
    toke_type : str = "bearer"
    customer_id : int