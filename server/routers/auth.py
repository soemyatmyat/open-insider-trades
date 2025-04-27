from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm, SecurityScopes
from schemas import auth as auth_schema
from services import auth as auth_mgr
from typing import Annotated
from routers.utils import exceptions

from sqlalchemy.orm import Session
from db import get_db

router = APIRouter()

@router.post("/token", response_model=auth_schema.Token, tags=["auth"], include_in_schema=False) # return bearer token
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session=Depends(get_db)) -> auth_schema.Token:
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
    access_token = auth_mgr.create_access_token(data={"sub": user.client_id},scopes=scopes) # create access token with sub as client_id and scopes
    return auth_schema.Token(access_token=access_token, token_type="bearer") # return access token and token type

@router.post("/logout", include_in_schema=True) 
async def logout(token: str = Depends(auth_mgr.oauth2_scheme)):
    # revoke the token access (it will expire by default in 30 mins anyway)
    auth_mgr.revoke_access_token(token)

async def get_current_client(security_scopes: SecurityScopes, token: Annotated[str, Depends(auth_mgr.oauth2_scheme)], db: Session = Depends(get_db)):
    '''
    this function will be called for authorization, similar to @app.get("/protected")
    but this is faciliated with FastAPI: Depends(get_current_client)
    oath2_scheme is used to get the Bearer token from the request header
    if the token is invalid, missing or the user is not found, throw an exception
    '''
    token_data = auth_mgr.decode_access_token(token) # get the token data
    if token_data is None:
        raise exceptions.auth_exception("Could not validate credentials", headers={"WWW-Authenticate": f'Bearer scope="{security_scopes.scope_str}"'})
    
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise exceptions.forbidden_exception("Not enough permissions", headers={"WWW-Authenticate": f'Bearer scope="{security_scopes.scope_str}"'})

    # get the client_id from the token sub data if authorization is successful
    client = auth_mgr.get_client_by_id(db, client_id=token_data.sub) # {"sub": client_id}
    if client is None:
        raise exceptions.auth_exception
    return client # client_id, is_active, role
