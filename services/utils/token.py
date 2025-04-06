from datetime import datetime, timedelta, timezone 
from jose import JWTError, jwt
from schemas import auth as schema
import settings

BLACKLIST = set()

# jwt is based64 encoded. anyone can decode the token and use its data. But only the server can verify it's authenticity using the JWT_SECRET_KEY
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy() # data={"sub": client_id}
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else: # default 30 mins (in settings)
        expire = datetime.now(timezone.utc) + timedelta(minutes=float(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp":expire}) # to_encode={"sub": client_id, "exp": expire}
    # encode jwt with secrect key and algorithm, and return it 
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def revoke_token(token: str):
    BLACKLIST.add(token)

def decode_access_token(token: str):
    if (token not in BLACKLIST):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            client_id: str = payload.get("sub")
            token_data = schema.TokenData(username=client_id)
        except JWTError: # when will this be triggered??
            return None
        return token_data  # return {"username": client_id}
    return None

