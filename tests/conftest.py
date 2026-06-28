import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.auth.security import hash_password

TEST_DB_FILE = "test_stockmate.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"

@pytest.fixture(name="db_session")
def db_session_fixture():
    """
    Creates an isolated file-based test database, seeds standard test accounts,
    and yields the session before dropping the tables and cleaning up the file.
    """
    # Clean up any leftover file
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    # Import all models to register them on Base.metadata
    from app.models.user import User
    from app.models.category import Category
    from app.models.product import Product
    from app.models.customer import Customer
    from app.models.sale import Sale
    from app.models.sale_item import SaleItem
    from app.models.audit_log import AuditLog
    
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Seed mock test accounts
    test_owner = User(
        full_name="Test Owner",
        email="testowner@stockmate.com",
        password=hash_password("owner123"),
        role="Owner"
    )
    test_employee = User(
        full_name="Test Employee",
        email="testemployee@stockmate.com",
        password=hash_password("employee123"),
        role="Employee"
    )
    db.add(test_owner)
    db.add(test_employee)
    db.commit()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    
    # Clean up file
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass

@pytest.fixture(name="client")
def client_fixture(db_session):
    """
    Overrides the DB dependency inside app router routes with our mock session
    and returns a FastAPI TestClient.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
