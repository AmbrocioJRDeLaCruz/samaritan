from sqlmodel import SQLModel

class UserCreate(SQLModel):
  name: str
  email: str
  password: str
  
class UserLogin(SQLModel):
  email: str
  password: str

class BeneficiaryCreate(SQLModel):
  name: str
  phone: str | None = None
  location: str | None = None
  household_size: int | None = None
  
class BeneficiaryUpdate(SQLModel):
  name: str | None = None
  phone: str | None = None
  location: str | None = None
  household_size: int | None = None