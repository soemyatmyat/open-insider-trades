from fastapi import APIRouter, Depends, HTTPException
from schemas import transaction as schema
from services import transaction as transactMgr
from sqlalchemy.orm import Session 
from db import get_db

router = APIRouter()

@router.get("", response_model=list[schema.Transaction]) 
async def retrieve_by_ticker(transaction_params: schema.TransactionParams = Depends(), db: Session=Depends(get_db)):

  # from_date and to_date check
  if transaction_params.from_date and transaction_params.to_date and transaction_params.from_date  > transaction_params.to_date : 
      raise HTTPException(status_code=400, detail="from_date cannot be after to_date.")

  # the ticker input validation
  existing_ticker = transactMgr.retrieve_by_ticker(db, transaction_params.ticker)
  if not existing_ticker:
    raise HTTPException(status_code=404, detail="No data found, symbol may be delisted.")
  
  transactions = transactMgr.retrieve_transactions(
    db, 
    transaction_params.ticker,
    transaction_params.from_date,
    transaction_params.to_date
  )
  return transactions or []