from fastapi import APIRouter, Depends, Security
from schemas import transaction as schema
from schemas import auth as authSchema
from services import transaction as transact_mgr
from services import auth as auth_mgr
from sqlalchemy.orm import Session 
from db import get_db
from datetime import datetime
import routers.utils.exceptions as exceptions
from routers.auth import get_current_client

router = APIRouter()

@router.get("/generate_client_id", response_model=authSchema.ClientCreate, tags=["Admin"])# admin api endpoint
async def generate_client_id(current_user: authSchema.Client = Security(get_current_client, scopes=["admin"]),db: Session = Depends(get_db)):
  try:
    client_id = auth_mgr.generate_client_id(db)
    return client_id
  except Exception as e:
    print(e)
    raise exceptions.internal_server_exception(detail="A generic error occurred on the server.")

@router.get("/bootstrap", tags=["Admin"]) # admin api endpoint
async def bootstrap(current_user: authSchema.Client = Security(get_current_client, scopes=["admin"]),data_params: schema.DataParams = Depends(), db: Session = Depends(get_db)):
  try:
    start_year = data_params.start_year  # Extract the start_year from the validated Pydantic model
    transact_mgr.force_refresh(db, data_params.start_year) # Call the force_refresh function
  except Exception as e:
    raise exceptions.internal_server_exception(detail="A generic error occurred on the server.")

@router.get("/daily_sync", tags=["Admin"]) # admin api endpoint (for testing purpose)
async def daily_sync(db: Session = Depends(get_db)):
  print(f"Running daily sync at {datetime.now()}")
  try:
    current_year = datetime.now().year # Get the current year
    transact_mgr.bootstrap_data(db, current_year, True) # Call the bootstrap_data function
  except Exception as e:
    raise exceptions.internal_server_exception(detail="A generic error occurred on the server.")
  

