from datetime import datetime, timedelta, timezone 
from jose import JWTError, jwt
from schemas import auth as authSchema
import secrets
import settings

BLACKLIST = set()

# jwt is based64 encoded. anyone can decode the token and use its data. But only the server can verify it's authenticity using the JWT_SECRET_KEY
def create_access_token(data: dict, scopes: list[str], expires_delta: timedelta | None = None):
  to_encode = data.copy() # data={"sub": client_id}
  if expires_delta:
    expire = datetime.now(timezone.utc) + expires_delta
  else: # default 30 mins (in settings)
    expire = datetime.now(timezone.utc) + timedelta(minutes=float(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
  to_encode.update({"scopes": scopes,"exp":expire}) # to_encode={"sub": client_id, "scope": read, "exp": expire}
  # encode jwt with secrect key and algorithm, and return it 
  encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
  return encoded_jwt


def create_token():
  ''' Return a random URL-safe text string, in Base64 encoding'''
  return secrets.token_urlsafe(32)  # Generate a random string as refresh token

def revoke_token(token: str):
    BLACKLIST.add(token)

def decode_access_token(token: str):
  if (token not in BLACKLIST):
    try:
      payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
      client_id: str = payload.get("sub")
      token_scopes = payload.get("scopes", [])
      token_data = authSchema.TokenData(sub=client_id, scopes=token_scopes)
    except JWTError: # when will this be triggered??
      return None
    return token_data  # return {"sub": client_id, "scopes": token_scopes}
  return None

