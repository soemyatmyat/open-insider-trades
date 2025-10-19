import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env')) # take environment variables from .env.

# ============================
# Environment Constants
# ============================
ORIGINS=os.environ.get("ORIGINS", "*").split(",") # for CORS, default is all origins
BASEDIR_APP=os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH=os.environ.get("DATABASE_PATH")
SECRET_KEY=os.environ.get("SECRET_KEY") 
ALGORITHM=os.environ.get("ALGORITHM") 
ACCESS_TOKEN_EXPIRE_MINUTES=os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "false").lower() == "true" # should be True in production with HTTPS
COOKIE_DOMAIN=os.environ.get("COOKIE_DOMAIN", "localhost") # should be set to the domain of the app in production
SQLALCHEMY_DATABASE_URL=os.environ.get("SQLALCHEMY_DATABASE_URL")
REDIS_URL=os.environ.get("REDIS_URL")
REDIS_PASSWORD=os.environ.get("REDIS_PASSWORD")
REDIS_PORT=os.environ.get("REDIS_PORT")
REDIS_EX=os.environ.get("REDIS_EX", 600)  # Default to 600 seconds if not set

# ============================
# Rate Limiter Constants
# ============================
RATE_LIMIT_CONFIG = {
  "client": {"limit": 5, "window_seconds": 60},
  "admin": {"limit": 50, "window_seconds": 60},
  "super_admin": {"limit": 100, "window_seconds": 60},
}

# ============================
# BSoup Configurable Constants
# ============================
BASE_URL=os.environ.get("BASE_URL")
DEFAULT_FILLING_DAYS=os.environ.get("DEFAULT_FILLING_DAYS")
TRADE_DATE_FILTER=os.environ.get("TRADE_DATE_FILTER")
MAX_WORKERS=os.environ.get("MAX_WORKERS")
OUTPUT_DIR=os.path.join(basedir, os.environ.get("OUTPUT_DIR"))
COLUMN_HEADERS=os.environ.get("COLUMN_HEADERS")
MAX_ROWS=os.environ.get("MAX_ROWS")

# ============================
# API Constants
# ============================
SUPER_ADMIN_ID = os.environ.get("SUPER_ADMIN_ID")
SUPER_ADMIN_SECRET = os.environ.get("SUPER_ADMIN_SECRET")

# ============================
# DAILY SYNC Constants
# ============================
DAILY_SYNC_HOUR=os.environ.get("DAILY_SYNC_HOUR", 21) # default is 20 (9 PM)
MISFIRE_GRACE_TIME=os.environ.get("MISFIRE_GRACE_TIME", 3600) # default is 3600 seconds (1 hour)