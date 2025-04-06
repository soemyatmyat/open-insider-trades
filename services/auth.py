from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session 
from passlib.context import CryptContext
import services.utils.token as jwtoken
import uuid
import secrets
from models import client as model
from schemas import auth as schema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # password-hash before storing
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token") # redriect to this endpoint to get the token

def generate_client_id(db: Session) -> schema.ClientCreate:
  client_id = str(uuid.uuid4())
  client_secret, hashed_secret = generate_client_secret()
  # convert to ORM model
  db_client = model.Client(id=client_id, hashed_secret=hashed_secret, is_active=True)
  db.add(db_client)
  db.commit()
  db.refresh(db_client)
  if db_client:
    return schema.ClientCreate(client_id=db_client.id, client_secret=client_secret, is_active=db_client.is_active)
  return None

def generate_client_secret():
  # Generate a random string as client secret
  secret = secrets.token_urlsafe(32)  # 32 bytes of random data, URL-safe base64 encoded
  # Hash the secret before storing it in the database
  hashed_secret = pwd_context.hash(secret)
  return secret, hashed_secret

def get_client(db: Session, client_id: int):
  return db.query(model.Client).filter(model.Client.id == client_id).first()

def get_client_by_id(db: Session, client_id: str) -> schema.ClientId:
  client = db.query(model.Client).filter(model.Client.id == client_id).first()
  if client:
    return schema.ClientId(client_id=client.id, is_active=client.is_active)
  return None

def authenticate_client(db: Session, username: str, password: str):
  client = get_client_by_id(db, client_id=username)
  if not client:
    return False
  db_client = get_client(db, client.client_id)
  if not client.is_active and not pwd_context.verify(password, db_client.hashed_secret):
    return False
  return client # return the client with id and status
  
def create_access_token(data: dict, expires_delta: int = None):
  return jwtoken.create_access_token(data, expires_delta)

def decode_access_token(token: str):
  return jwtoken.decode_access_token(token)

def revoke_access_token(token: str):
  jwtoken.revoke_token(token)
