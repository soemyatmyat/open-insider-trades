from db import Base
from sqlalchemy import Column, Integer, String, Date, Numeric, TIMESTAMP
import uuid

class Transaction(Base):
  __tablename__ = 'transactions'

  id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
  x = Column(String(1))
  filing_date = Column(TIMESTAMP)
  trade_date = Column(Date)
  ticker = Column(String(10), index=True)
  company_name = Column(String)
  insider_name = Column(String)
  insider_title = Column(String)
  trade_type = Column(String(20))
  price = Column(Numeric(10, 2))
  qty = Column(Integer)
  owned = Column(Integer)
  delta_owned = Column(String(20))
  value = Column(Numeric(15, 2))