from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, UTC

from models import client as model
import settings

class RateLimitExceededException(Exception):
  pass

def validate_rate_limit(current_user, db: Session):
  role = current_user.role or "client"  # default to client
  rate_config = settings.RATE_LIMIT_CONFIG.get(role, settings.RATE_LIMIT_CONFIG["client"]) # default to client

  now = datetime.now(UTC)
  window_start = now - timedelta(seconds=rate_config["window_seconds"])
  # Delete old timestamps (older than 60s or windows_seconds)
  db.query(model.Request_Log).filter(
    model.Request_Log.client_id == current_user.client_id,
    model.Request_Log.timestamp < window_start
  ).delete()
  # Count how many remain
  count = db.query(model.Request_Log).filter(
    model.Request_Log.client_id == current_user.client_id,
    model.Request_Log.timestamp >= window_start
  ).count()
  # Block if it is ≥ limit, otherwise, allow and log the new timestamp
  if count >= rate_config["limit"]:
    raise RateLimitExceededException()
  else:
    # Log the request
    new_request = model.Request_Log(client_id=current_user.client_id)
    db.add(new_request)
    db.commit() 
    db.refresh(new_request)