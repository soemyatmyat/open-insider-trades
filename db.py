from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker 
import settings

# Create a databse engine
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} # because we are going to do async calls, only for SQLite
)

# Create a sessionmaker to interact with the database (each instance of the sessionLocal will be a database session)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Create a base class for all database models when using SQLAlchemy's ORM (Object Relational Mapper)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()