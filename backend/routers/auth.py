from datetime import datetime, timedelta, timezone
import jwt

from fastapi import APIRouter, Depends, HTTPException
from pwdlib import PasswordHash
from sqlmodel import Session, select

from ..database import get_session
from ..models import User
from ..schemas import UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])

password_hash = PasswordHash.recommended()

SECRET_KEY = "change-this-later"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(user_id: int):
  expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  
  payload = {
    "sub": str(user_id),
    "exp": expire
  }
  
  return jwt.encode(
    payload,
    SECRET_KEY,
    algorithm=ALGORITHM
  )

@router.post("/register")
def register(user_data: UserCreate, session: Session = Depends(get_session)):
  existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
  
  if existing_user:
    raise HTTPException(status_code=400, detail="Email already registered")
  
  hashed_password = password_hash.hash(user_data.password)
  
  user = User(
    name=user_data.name,
    email=user_data.email,
    password_hash=hashed_password,
    role="volunteer"
  )
  
  session.add(user)
  session.commit()
  session.refresh(user)

  return {
    "id": user.id,
    "name": user.name,
    "email": user.email,
    "role": user.role
  }

@router.post("/login")
def login(user_data: UserLogin, session: Session = Depends(get_session)):
  
  user = session.exec(select(User).where(User.email == user_data.email)).first()
  
  if not user or not password_hash.verify(user_data.password, user.password_hash):
    raise HTTPException(status_code=401, detail="Invalid email or password")
  
  access_token = create_access_token(user.id)
  
  return {
    "access_token": access_token,
    "token_type": "bearer"
  }