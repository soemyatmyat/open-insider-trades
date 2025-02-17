from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID, uuid4
from enum import Enum 

class TransactionType(Enum):
  S = "S - Sale"
  SOE = "S - Sale+OE"
  P = "P - Purchase"

class XType(Enum):
  M = "M" # Multiple transactions in filing 
  D = "D" # Derivative transaction in filing (usually option exercise)
  A = "A" # Amended filing 
  E = "E" # Error detected in filing

class Transaction(BaseModel):
  # id: UUID = uuid4() # this should be omitted
  x_type: XType
  filing_date: datetime
  trade_date: date
  ticker: str
  company_name: str
  insider_name: str
  title: str
  trade_type: TransactionType
  price: float
  qty: int
  owned: int
  data_owned: float
  value: float
