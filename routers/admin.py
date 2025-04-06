from fastapi import APIRouter, Depends
from schemas import transaction as schema
from schemas import auth as auth_schema
from services import transaction as transactMgr
from services import auth as authMgr
from sqlalchemy.orm import Session 
from db import get_db
from datetime import datetime
import routers.utils.exceptions as exceptions

router = APIRouter()

@router.get("/generate_client_id", response_model=auth_schema.ClientCreate, tags=["Admin"])# admin api endpoint
async def generate_client_id(db: Session = Depends(get_db)):
  try:
    client_id = authMgr.generate_client_id(db)
    return client_id
  except Exception as e:
    print(e)
    raise exceptions.internal_server_exception(detail="A generic error occurred on the server.")

@router.get("/bootstrap", tags=["Admin"]) # admin api endpoint
async def bootstrap(data_params: schema.DataParams = Depends(), db: Session = Depends(get_db)):
  try:
    start_year = data_params.start_year  # Extract the start_year from the validated Pydantic model
    transactMgr.force_refresh(db, data_params.start_year) # Call the force_refresh function
  except Exception as e:
    raise exceptions.internal_server_exception(detail="A generic error occurred on the server.")

# @router.get("/daily_sync", tags=["Admin"]) # admin api endpoint (for testing purpose)
async def daily_sync(db: Session = Depends(get_db)):
  try:
    current_year = datetime.now().year # Get the current year
    transactMgr.bootstrap_data(db, current_year, True) # Call the bootstrap_data function
  except Exception as e:
    raise exceptions.internal_server_exception(detail="A generic error occurred on the server.")
  

