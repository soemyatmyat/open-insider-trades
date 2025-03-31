from fastapi import APIRouter, Depends, HTTPException
from schemas import transaction as schema
from services import transaction as transactMgr
from sqlalchemy.orm import Session 
from db import get_db
from datetime import datetime, timedelta, date

router = APIRouter()

@router.get("/bootstrap", tags=["Admin"]) # admin api endpoint
async def bootstrap(data_params: schema.DataParams = Depends(), db: Session = Depends(get_db)):
  try:
    start_year = data_params.start_year  # Extract the start_year from the validated Pydantic model
    transactMgr.force_refresh(db, data_params.start_year) # Call the force_refresh function
  except Exception as e:
    raise HTTPException(status_code=500, detail="A generic error occurred on the server.")

# @router.get("/daily_sync", tags=["Admin"]) # admin api endpoint (for testing purpose)
async def daily_sync(db: Session = Depends(get_db)):
  try:
    current_year = datetime.now().year # Get the current year
    transactMgr.bootstrap_data(db, current_year, True) # Call the bootstrap_data function
  except Exception as e:
    raise HTTPException(status_code=500, detail="A generic error occurred on the server.")
  

