from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from db import engine, Base 

app = FastAPI()

# Configure CORS 
origins = ["*"] # this need to be changed later, to only allow whitelisted IPs 
# origins = ["https://finance.boring-is-good.com"]
app.add_middleware(
  CORSMiddleware,
  allow_origins=origins, 
  allow_credentials=True, # Credentials (Authorization headers, Cookies, etc).
  allow_methods=["GET","POST","PUT","DELETE","OPTIONS"], # Specify the allowed HTTP methods
  allow_headers=["*"], # Specify the allowed headers 
)

# When accessing through the root path, redirect the users to Swagger
# should it be to interactive docs via Swagger UI (/docs) OR ReDoc (/redoc).
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
  return RedirectResponse(url="/docs")

# Create all the tables (if it doesn't already exist) defined in the Base class'metadata within the connected database 
Base.metadata.create_all(bind=engine) 
