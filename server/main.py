from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from routers.transaction import router as transact_router
from routers.admin import router as admin_router
from routers.auth import router as auth_router
from db import engine, Base 
from services.seeding import seed_super_admin

app = FastAPI()

# Configure CORS 
origins = ["*"] # this need to be changed later, to only allow whitelisted IPs 
# origins = ["https://finance.boring-is-good.com"]
app.add_middleware(
  CORSMiddleware,
  allow_origins=origins, 
  allow_credentials=True, # Allow Credentials (Authorization headers, Cookies, etc) to be included in the requests
  allow_methods=["GET","POST","PUT","DELETE","OPTIONS"], # Specify the allowed HTTP methods
  allow_headers=["*"], # Specify the allowed headers 
)

# When accessing through the root path, redirect the users to Swagger
# should it be to interactive docs via Swagger UI (/docs) OR ReDoc (/redoc).
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
  return RedirectResponse(url="/docs")

app.include_router(transact_router, prefix="/insider_trades")
app.include_router(admin_router, prefix="/admin")
app.include_router(auth_router, prefix="/auth")

# Create all the tables (if it doesn't already exist) defined in the Base class'metadata within the connected database 
Base.metadata.create_all(bind=engine) 
# Create necessary seeds for the database
seed_super_admin()