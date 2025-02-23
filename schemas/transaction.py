from typing import Optional
from pydantic import BaseModel
from datetime import date, datetime
from enum import Enum 
import uuid

class TransactionParams(BaseModel):
   ticker: str 
   from_date: Optional[date]
   to_date: Optional[date]

class DataParams(BaseModel):
    start_year: int

class TransactionType(Enum):
  S = "S - Sale"
  SOE = "S - Sale+OE"
  P = "P - Purchase"

class Transaction(BaseModel):
  id: str   
  x: Optional[str] 
  filing_date: Optional[datetime]
  trade_date: date
  ticker: str
  company_name: Optional[str]
  insider_name: Optional[str]
  insider_title: Optional[str]
  trade_type: Optional[TransactionType]
  price: Optional[float]
  qty: Optional[int]
  owned: Optional[int]
  delta_owned: Optional[str]
  value: Optional[float]

  class Config:
    orm_mode = True  # Important to tell Pydantic to convert ORM objects to Pydantic models

