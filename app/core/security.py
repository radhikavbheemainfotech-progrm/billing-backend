from passlib.context import CryptContext
from jose import jwt , JWTError
from datetime import datetime,timedelta
from typing import Optional
from app.core.config import settings


pwd_context = CryptContext(schemes = ["bcrypt"],deprecated = "auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password : str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_token(token:str) -> str:
    return pwd_context.hash(token)

def verify_token_hash(plain_token:str, hashed_token: str) -> bool:
    return pwd_context.verify(plain_token,hashed_token)


def create_access_token(data:dict,expires_delta: Optional[timedelta] = None) -> str:

    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire,"type": "access"})
    return jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type" :"refresh"})
    return jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)


def decode_token(token :str,token_type: str = "access") -> Optional[dict]:
    try:
        payload =  jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None
