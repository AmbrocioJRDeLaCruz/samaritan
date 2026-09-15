from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
  
  id: int | None = Field(default=None, primary_key=True)
  name: str | None = Field(default=None, index=True)
  email: str = Field(unique=True, nullable=False)
  password_hash: str = Field(nullable=False)
  role: str = Field(default="volunteer")