import redis 
import settings
from fastapi import Depends

# Create Redis connection pool
def create_redis_pool() -> redis.ConnectionPool:
  return redis.ConnectionPool(
    host=settings.REDIS_URL,  
    password=settings.REDIS_PASSWORD,
    port=settings.REDIS_PORT, 
    db=0, 
    decode_responses=True  
) 

# Get Redis client using the connection pool
def get_redis_client(pool: redis.ConnectionPool = Depends(create_redis_pool)) -> redis.Redis:
  try:
    return redis.Redis(connection_pool=pool)
  except redis.ConnectionError: # if error: send None
    return None