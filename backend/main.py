from fastapi import FastAPI
from sqlmodel import SQLModel

from .database import engine
from . import models
from .routers import auth

app = FastAPI()

def create_db_and_tables():
  SQLModel.metadata.create_all(engine)
  
create_db_and_tables()

app.include_router(auth.router)
  
@app.get("/")
def root():
  return {"message": "Samaritan API is running"}