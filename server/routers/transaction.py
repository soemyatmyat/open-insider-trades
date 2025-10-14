import redis
from services import redis_client 
from fastapi import APIRouter, Depends, Security
from schemas import transaction as tranact_schema
from schemas import auth as authSchema
from services import transaction as transact_mgr
from services import rate_limiter as rate_limiter
from sqlalchemy.orm import Session 
from db import get_db
from routers.auth import get_current_client
from routers.utils import exceptions

router = APIRouter()

'''
Retrieve insider transactions by ticker
params: from_date, to_date, transaction_type
response: list of transactions
permission: read
dependencies: get_current_client, get_db, get_redis_client
'''
@router.get("/{ticker_id}", response_model=list[tranact_schema.Transaction]) 
async def retrieve_by_ticker(ticker_id: str,
  params: tranact_schema.TransactionParams = Depends(), 
  current_user: authSchema.Client = Security(get_current_client, scopes=["read"]), 
  db: Session=Depends(get_db),
  redis_client: redis.Redis = Depends(redis_client.get_redis_client)
  ):

  # rate limit validation
  try:
    rate_limiter.validate_rate_limit(current_user, db, redis_client)
  except rate_limiter.RateLimitExceededException:
    raise exceptions.too_many_requests_exception("Rate limit exceeded. Please try again later.")

  # from_date and to_date check
  if params.from_date and params.to_date and params.from_date  > params.to_date : 
    raise exceptions.bad_request_exception("from_date cannot be after to_date.")

  # the ticker input validation
  ticker_id = ticker_id.upper()
  existing_ticker = transact_mgr.retrieve_by_ticker(db, ticker_id)
  if not existing_ticker:
    raise exceptions.not_found_exception("No data found, symbol may be delisted.")
  
  transactions = transact_mgr.retrieve_transactions(
    db, 
    ticker_id,
    params.from_date,
    params.to_date,
    params.transaction_type
  )
  return transactions or []

'''
Retrieve insider transactions by date range
params: from_date, to_date, transaction_type
response: list of transactions
permission: read
dependencies: get_current_client, get_db, get_redis_client
'''
@router.get("", response_model=list[tranact_schema.Transaction]) 
async def retrieve_by_date_range(
  params: tranact_schema.TransactionDateRange = Depends(), 
  current_user: authSchema.Client = Security(get_current_client, scopes=["read"]), 
  db: Session=Depends(get_db),
  redis_client: redis.Redis = Depends(redis_client.get_redis_client)
  ):

  # rate limit validation
  try:
    rate_limiter.validate_rate_limit(current_user, db, redis_client)
  except rate_limiter.RateLimitExceededException:
    raise exceptions.too_many_requests_exception("Rate limit exceeded. Please try again later.")
  
  # from_date and to_date check
  if params.from_date and params.to_date and params.from_date  > params.to_date : 
    raise exceptions.bad_request_exception("from_date cannot be after to_date.")

  transactions = transact_mgr.retrieve_transactions(
    db, 
    "",
    params.from_date,
    params.to_date,
    params.transaction_type
  )
  return transactions or []
