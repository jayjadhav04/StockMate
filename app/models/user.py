import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # stores hashed password
    role = Column(String(20), nullable=False, default="Employee")  # "Owner" or "Employee"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
