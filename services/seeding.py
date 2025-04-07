# seeding.py
from fastapi import Depends
from sqlalchemy.orm import Session
from models import client as model
from db import SessionLocal
from passlib.context import CryptContext
import settings

# Set up password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_super_admin():
  db: Session = SessionLocal()
  try:
    existing = db.query(model.Client).filter(model.Client.id == settings.SUPER_ADMIN_ID).first()
    if existing:
      print("Super admin already exists.")
      return

    super_admin = model.Client(
      id=settings.SUPER_ADMIN_ID,
      hashed_secret=pwd_context.hash(settings.SUPER_ADMIN_SECRET),
      is_active=True,
      role="super_admin"
    )

    db.add(super_admin)
    db.commit()
    print("Super admin created successfully.")
  finally:
    db.close()

# if __name__ == "__main__":
#   seed_super_admin()
