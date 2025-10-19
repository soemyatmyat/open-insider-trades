from fastapi import APIRouter, Response, Header, Cookie, Depends
from fastapi.security import OAuth2PasswordRequestForm, SecurityScopes
from schemas import auth as auth_schema
from services import auth as auth_mgr
from typing import Annotated
from routers.utils import exceptions
import settings
from sqlalchemy.orm import Session
from db import get_db

router = APIRouter()
refresh_tokens_store = {}  # {refresh_token: user_id} -- in-memory store for refresh tokens, but it should be cached in redis

@router.post("/token", response_model=auth_schema.Token, tags=["auth"], include_in_schema=False) # return bearer token
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response, db: Session=Depends(get_db)) -> auth_schema.Token:
  '''
  this function will be called for authentication, when the user login with username and password
  the username and password will be passed to the form_data
  the form_data will be validated by FastAPI
  if the username and password are correct, return the access token
  if the username and password are incorrect, raise an exception
  '''
  user = auth_mgr.authenticate_client(db, form_data.username, form_data.password)
  if not user:
      raise exceptions.auth_exception("Incorrect username or password")
  scopes = ["read", "write", "admin"] if user.role == "super_admin" else ["read"]
  # create access token with sub as client_id and scopes
  access_token = auth_mgr.create_access_token(data={"sub": user.client_id},scopes=scopes) 

  # Set the new csrf token as a NonHttpOnly, Secure cookie
  set_csrf_token_cookie(user, response)
  # Set the new refresh token as an HttpOnly, Secure cookie
  set_refresh_token_cookie(user, response, refresh_token)
  # return access token and token type
  return auth_schema.Token(access_token=access_token, token_type="bearer") 

@router.post("/refresh", response_model=auth_schema.Token, tags=["auth"], include_in_schema=False) # return bearer token
# refresh_token = request.cookies.get("refresh_token")  # Get the refresh token from the cookie
async def refresh_token(
  response: Response, 
  db: Session=Depends(get_db),
  refresh_token: str = Cookie(None),
  csrf_cookie: str = Cookie(None, alias="csrf_token"),
  csrf_header: str = Header(None, alias="X-CSRF-TOKEN")
  ) -> auth_schema.Token:

  # print(f"csrf_cookie: {csrf_cookie}, csrf_header: {csrf_header}, refresh_token: {refresh_token}")
  if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
    raise exceptions.forbidden_exception("CSRF token mismatch")
  
  user_id = refresh_tokens_store.get(refresh_token)
  if not user_id:
    raise exceptions.auth_exception("Invalid refresh token.")
  
  user = auth_mgr.get_client_by_id(db, user_id)
  if not user:
    raise exceptions.auth_exception("User not found with the provided refresh token.")
  scopes = ["read", "write", "admin"] if user.role == "super_admin" else ["read"]
  access_token = auth_mgr.create_access_token(data={"sub": user.client_id},scopes=scopes) 

  # Set the new csrf token as a NonHttpOnly, Secure cookie
  set_csrf_token_cookie(user, response)
  # Set the new refresh token as an HttpOnly, Secure cookie
  del refresh_tokens_store[refresh_token]
  set_refresh_token_cookie(user, response, refresh_token)
  # return access token and token type
  return auth_schema.Token(access_token=access_token, token_type="bearer") 

@router.post("/logout", include_in_schema=True) 
async def logout(token: str = Depends(auth_mgr.oauth2_scheme)):
    # revoke the token access (it will expire by default in 30 mins anyway)
    auth_mgr.revoke_access_token(token)

def set_csrf_token_cookie(user, response: Response):
    csrf_token = auth_mgr.create_token()  # Generate a new CSRF token
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/",  # Set the path to root so it is sent with every request
        domain=settings.COOKIE_DOMAIN,  # Set the domain to the same as the app
        secure=settings.COOKIE_SECURE,
        httponly=False,
        samesite="None"
    )

def set_refresh_token_cookie(user, response: Response, refresh_token: str):
  refresh_token = auth_mgr.create_token()
  refresh_tokens_store[refresh_token] = user.client_id  # Store the refresh token in memory (or use a more persistent store like Redis)
  response.set_cookie(
      key="refresh_token",
      value=refresh_token,
      max_age=7 * 24 * 60 * 60,  # 7 days
      path="/",  # Set the path to root so it is sent with every request
      secure=settings.COOKIE_SECURE,
      httponly=True,
      samesite="None"
  )

async def get_current_client(security_scopes: SecurityScopes, token: Annotated[str, Depends(auth_mgr.oauth2_scheme)], db: Session = Depends(get_db)):
    '''
    this function will be called for authorization, similar to @app.get("/protected")
    but this is faciliated with FastAPI: Depends(get_current_client)
    oath2_scheme is used to get the Bearer token from the request header
    if the token is invalid, missing or the user is not found, throw an exception
    '''
    token_data = auth_mgr.decode_access_token(token) # get the token data
    if token_data is None:
        raise exceptions.auth_exception("Token has expired.", headers={"WWW-Authenticate": f'Bearer scope="{security_scopes.scope_str}"'})
    
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise exceptions.forbidden_exception("Not enough permissions", headers={"WWW-Authenticate": f'Bearer scope="{security_scopes.scope_str}"'})

    # get the client_id from the token sub data if authorization is successful
    client = auth_mgr.get_client_by_id(db, client_id=token_data.sub) # {"sub": client_id}
    if client is None:
        raise exceptions.auth_exception
    return client # client_id, is_active, role
