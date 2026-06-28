from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Determine if we're using SQLite or MySQL to apply specific engine configurations
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

connect_args = {}
if is_sqlite:
    # SQLite-specific connection arguments to support multi-threaded operations in FastAPI
    connect_args["check_same_thread"] = False

# Create the engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True  # Automatically checks connection health before executing queries
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for models
Base = declarative_base()

# Database session dependency for routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
