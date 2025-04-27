from typing import Optional
from pydantic import BaseModel
from datetime import date, datetime
from enum import Enum 

class TransactionType(Enum):
  S = "S - Sale"
  SOE = "S - Sale+OE"
  P = "P - Purchase"

class TransactionParams(BaseModel):
  ticker: str 
  from_date: Optional[date] = None
  to_date: Optional[date] = None
  transaction_type: Optional[TransactionType] = None 

class TransactionDateRange(BaseModel):
  from_date: date
  to_date: date
  transaction_type: Optional[TransactionType] = None 

class DataParams(BaseModel):
    start_year: int

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
  from_attribute = True  # Important to tell Pydantic to convert ORM objects to Pydantic models

