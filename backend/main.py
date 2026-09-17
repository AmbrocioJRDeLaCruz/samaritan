from fastapi import FastAPI
from sqlmodel import SQLModel
from fastapi.middleware.cors import CORSMiddleware

from .database import engine
from . import models
from .routers import auth, beneficiaries

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

def create_db_and_tables():
  SQLModel.metadata.create_all(engine)
  
create_db_and_tables()

app.include_router(auth.router)
app.include_router(beneficiaries.router)
  
@app.get("/")
def root():
  return {"message": "Samaritan API is running"}