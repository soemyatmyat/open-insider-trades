import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env')) # take environment variables from .env.

BASEDIR_APP=os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH=os.environ.get("DATABASE_PATH")
SECRET_KEY=os.environ.get("SECRET_KEY") 
ALGORITHM=os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES=os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
SQLALCHEMY_DATABASE_URL=os.environ.get("SQLALCHEMY_DATABASE_URL")