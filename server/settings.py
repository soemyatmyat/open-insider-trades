import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env')) # take environment variables from .env.

# ============================
# Environment Constants
# ============================
BASEDIR_APP=os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH=os.environ.get("DATABASE_PATH")
SECRET_KEY=os.environ.get("SECRET_KEY") 
ALGORITHM=os.environ.get("ALGORITHM") 
ACCESS_TOKEN_EXPIRE_MINUTES=os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
SQLALCHEMY_DATABASE_URL=os.environ.get("SQLALCHEMY_DATABASE_URL")
REDIS_URL=os.environ.get("REDIS_URL")
REDIS_PASSWORD=os.environ.get("REDIS_PASSWORD")
REDIS_PORT=os.environ.get("REDIS_PORT")
REDIS_EX=os.environ.get("REDIS_EX")

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
OUTPUT_FILE=os.path.join(basedir, os.environ.get("OUTPUT_FILE"))
COLUMN_HEADERS=os.environ.get("COLUMN_HEADERS")
MAX_ROWS=os.environ.get("MAX_ROWS")

# ============================
# API Constants
# ============================
SUPER_ADMIN_ID = os.environ.get("SUPER_ADMIN_ID")
SUPER_ADMIN_SECRET = os.environ.get("SUPER_ADMIN_SECRET")