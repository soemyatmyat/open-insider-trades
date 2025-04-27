from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, UTC
import redis, json, time

from models import client as model
import settings

class RateLimitExceededException(Exception):
  pass

def validate_rate_limit_with_redis(redis_client: redis.Redis, redis_key: str, max_api_count: int, rate_windows_seconds: int):
  # Check if the key exists in Redis
  try:
    if (redis_client.ping()):
      print("Redis is available")
      if not redis_client.exists(redis_key):
        redis_client.set(redis_key, 1, ex=rate_windows_seconds)  # set value 1 with expiry of window_seconds
      else:
        redis_client.incrby(redis_key, 1) # increment the value
      print("Redis key: ", redis_key)
      print("Redis value: ", redis_client.get(redis_key))
      count = int(redis_client.get(redis_key))
      if count >= max_api_count:
        raise RateLimitExceededException()
      return True
  except redis.exceptions.ConnectionError as e:
    print("error: Could not connect to Redis: ", e)
    return False

def validate_rate_limit_with_sqlite(db: Session, current_user_id: str, max_api_count: int, rate_windows_seconds: int):
  # Fallback to sqlite3 if Redis is not available
  now = datetime.now(UTC)
  window_start = now - timedelta(seconds=rate_windows_seconds)
  print("Current User id: ", current_user_id, ", Window start: ", window_start)
  # Delete old timestamps (older than the rate window)
  db.query(model.Request_Log).filter(
    model.Request_Log.client_id == current_user_id,
    model.Request_Log.timestamp < window_start
  ).delete()
  
  # Count how many requests remain in the window
  count = db.query(model.Request_Log).filter(
    model.Request_Log.client_id == current_user_id,
    model.Request_Log.timestamp >= window_start
  ).count()
  print("Count: ", count)

  # Block if the count is ≥ limit, otherwise, allow and log the new timestamp
  if count >= max_api_count:
    raise RateLimitExceededException()
  else:
    # Log the request    
    new_request = model.Request_Log(client_id=current_user_id)
    db.add(new_request)
    db.commit() 
    db.refresh(new_request)

def validate_rate_limit(current_user, db: Session, redis_client: redis.Redis):
  # Fetch the rate limit configuration based on the user's role
  role = current_user.role or "client"  # default to client
  rate_config = settings.RATE_LIMIT_CONFIG.get(role, settings.RATE_LIMIT_CONFIG["client"]) # default to client
  max_api_count = rate_config["limit"]
  rate_windows_seconds = rate_config["window_seconds"]

  # Redis key is a combination of client_id and the current time divided by the window size
  redis_bucket_num = int(time.time()) // rate_windows_seconds  # convert to Unix epoch and divided it by window_seconds to get the window/bucket
  redis_key = f"rate_limit:{current_user.client_id}:{redis_bucket_num}" 

  # Perform rate limiting with Redis
  if validate_rate_limit_with_redis(redis_client, redis_key, max_api_count, rate_windows_seconds) == False:
    # Fallback to sqlite3 if Redis is not available
    current_user_id = current_user.client_id
    validate_rate_limit_with_sqlite(db, current_user_id, max_api_count, rate_windows_seconds)


