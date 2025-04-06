from pydantic import BaseModel

class ClientBase(BaseModel):
    pass

class ClientCreate(ClientBase): # should only be returned to the admin
    client_id: str
    client_secret: str
    is_active: bool 

class ClientId(ClientBase):
    client_id: str
    is_active: bool

class Token(BaseModel): 
    access_token: str 
    token_type: str 

class TokenData(BaseModel):
    username: str | None = None  # sub