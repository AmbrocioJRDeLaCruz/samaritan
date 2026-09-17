from sqlmodel import SQLModel

class UserCreate(SQLModel):
  name: str
  email: str
  password: str
  
class UserLogin(SQLModel):
  email: str
  password: str