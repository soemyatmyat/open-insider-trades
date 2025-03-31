from fastapi import APIRouter, Depends, HTTPException
from schemas import transaction as schema
from services import transaction as transactMgr
from sqlalchemy.orm import Session 
from db import get_db

router = APIRouter()

@router.get("/ticker", response_model=list[schema.Transaction]) 
async def retrieve_by_ticker(params: schema.TransactionParams = Depends(), db: Session=Depends(get_db)):

  # from_date and to_date check
  if params.from_date and params.to_date and params.from_date  > params.to_date : 
      raise HTTPException(status_code=400, detail="from_date cannot be after to_date.")

  # the ticker input validation
  existing_ticker = transactMgr.retrieve_by_ticker(db, params.ticker)
  if not existing_ticker:
    raise HTTPException(status_code=404, detail="No data found, symbol may be delisted.")
  
  print("THIS: ", params)
  
  transactions = transactMgr.retrieve_transactions(
    db, 
    params.ticker,
    params.from_date,
    params.to_date,
    params.transaction_type.value
  )
  return transactions or []

@router.get("", response_model=list[schema.Transaction]) 
async def retrieve_by_date_range(params: schema.TransactionDateRange = Depends(), db: Session=Depends(get_db)):
  
  # from_date and to_date check
  if params.from_date and params.to_date and params.from_date  > params.to_date : 
    raise HTTPException(status_code=400, detail="from_date cannot be after to_date.")

  transactions = transactMgr.retrieve_transactions(
    db, 
    "",
    params.from_date,
    params.to_date,
    params.transaction_type.value
  )
  return transactions or []