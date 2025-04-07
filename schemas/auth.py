from pydantic import BaseModel

class ClientBase(BaseModel):
    pass

class ClientCreate(ClientBase): # should only be returned to the admin
    client_id: str
    client_secret: str
    is_active: bool 
    role: str | None = None # values: client, admin, super_admin

class Client(ClientBase):
    client_id: str
    is_active: bool
    role: str | None = None # values: client, admin, super_admin

class Token(BaseModel): 
    access_token: str 
    token_type: str 

class TokenData(BaseModel):
    sub: str | None = None  # sub
    scopes: list[str] | None = None # scopes