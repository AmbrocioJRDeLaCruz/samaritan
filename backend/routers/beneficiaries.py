from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import Beneficiary, User
from ..schemas import BeneficiaryCreate, BeneficiaryUpdate
from .auth import get_current_user

router = APIRouter(prefix="/beneficiaries", tags=["beneficiaries"])

@router.post("/")
def create_beneficiary(data: BeneficiaryCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
  
  beneficiary = Beneficiary(**data.model_dump())
  
  session.add(beneficiary)
  session.commit()
  session.refresh(beneficiary)
  
  return beneficiary


@router.get("/")
def get_beneficiaries(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
  
  return session.exec(select(Beneficiary)).all()

@router.get("/{beneficiary_id}")
def get_beneficiary(beneficiary_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
  
  beneficiary = session.get(Beneficiary, beneficiary_id)
  
  if not beneficiary_id:
    raise HTTPException(
      status_code=404,
      detail="Beneficiary not found"
    )
  
  return beneficiary