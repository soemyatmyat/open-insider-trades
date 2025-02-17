from db import Base
from sqlalchemy import Column, Integer, String, Date, Numeric, TIMESTAMP
from uuid import uuid4

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(uuid4, primary_key=True, index=True)
    x = Column(String(1))
    ticker = Column(String(10), index=True)
    company_name = Column(String)
    insider_name = Column(String)
    insider_title = Column(String)
    trade_type = Column(String(20))
    trade_date = Column(Date)
    price = Column(Numeric(10, 2))
    qty = Column(Integer)
    owned = Column(Integer)
    delta_owned = Column(String(20))
    value = Column(Numeric(15, 2))
    filing_date = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default="CURRENT_TIMESTAMP")

