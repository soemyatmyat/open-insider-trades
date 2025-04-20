from fastapi import APIRouter, Depends, Security
from schemas import transaction as tranactSchema
from schemas import auth as authSchema
from services import transaction as transactMgr
from services import ratelimiter as rateLimiter
from sqlalchemy.orm import Session 
from db import get_db
from routers.auth import get_current_client
from routers.utils import exceptions

router = APIRouter()

@router.get("/ticker", response_model=list[tranactSchema.Transaction]) 
async def retrieve_by_ticker(
  params: tranactSchema.TransactionParams = Depends(), 
  current_user: authSchema.Client = Security(get_current_client, scopes=["read"]), 
  db: Session=Depends(get_db)):

  # rate limit validation
  try:
    rateLimiter.validate_rate_limit(current_user, db)
  except rateLimiter.RateLimitExceededException:
    raise exceptions.too_many_requests_exception("Rate limit exceeded. Please try again later.")

  # from_date and to_date check
  if params.from_date and params.to_date and params.from_date  > params.to_date : 
    raise exceptions.bad_request_exception("from_date cannot be after to_date.")

  # the ticker input validation
  existing_ticker = transactMgr.retrieve_by_ticker(db, params.ticker)
  if not existing_ticker:
    raise exceptions.not_found_exception("No data found, symbol may be delisted.")
  
  transactions = transactMgr.retrieve_transactions(
    db, 
    params.ticker,
    params.from_date,
    params.to_date,
    params.transaction_type
  )
  return transactions or []

@router.get("", response_model=list[tranactSchema.Transaction]) 
async def retrieve_by_date_range(
  params: tranactSchema.TransactionDateRange = Depends(), 
  current_user: authSchema.Client = Security(get_current_client, scopes=["read"]), 
  db: Session=Depends(get_db)):

  # rate limit validation
  try:
    rateLimiter.validate_rate_limit(current_user, db)
  except rateLimiter.RateLimitExceededException:
    raise exceptions.too_many_requests_exception("Rate limit exceeded. Please try again later.")
  
  # from_date and to_date check
  if params.from_date and params.to_date and params.from_date  > params.to_date : 
    raise exceptions.bad_request_exception("from_date cannot be after to_date.")

  transactions = transactMgr.retrieve_transactions(
    db, 
    "",
    params.from_date,
    params.to_date,
    params.transaction_type.value
  )
  return transactions or []
