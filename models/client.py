from db import Base
from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
import uuid

class Client(Base):
  __tablename__ = 'clients'

  id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
  hashed_secret = Column(String)
  is_active = Column(Boolean, default=True)
  role = Column(String, default="client")  # values: client, admin, super_admin
  
  requests = relationship("Request_Log", back_populates="client")

class Request_Log(Base):
  __tablename__ = 'request_logs'

  id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
  client_id = Column(String, ForeignKey("clients.id"))
  timestamp = Column(DateTime, default=datetime.now(UTC))

  client = relationship("Client", back_populates="requests")