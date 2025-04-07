from db import Base
from sqlalchemy import Boolean, Column, String
import uuid

class Client(Base):
  __tablename__ = 'clients'

  id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
  hashed_secret = Column(String)
  is_active = Column(Boolean, default=True)
  role = Column(String, default="client")  # values: client, admin, super_admin