import os
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.customer import Customer
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.audit_log import AuditLog
from app.models.supplier import Supplier
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.auth.security import hash_password
from app.auth.dependencies import RedirectToLoginException, ForbiddenException
from app.utils.templates import templates

# Import Routers
from app.routers import auth, dashboard, category, product, customer, sale, charts, report, export, employee, audit, supplier, purchase

# Initialize the FastAPI app
_is_dev = settings.APP_ENV == "development"
app = FastAPI(
    title="StockMate API",
    description="StockMate - Inventory & Sales Management System API",
    version="1.0.0",
    docs_url="/docs" if _is_dev else None,    # Hidden in production
    redoc_url="/redoc" if _is_dev else None,  # Hidden in production
    debug=_is_dev
)

# Add HTTP middleware to disable caching for HTML responses (prevents back-button cache bypass)
@app.middleware("http")
async def add_cache_control_headers(request: Request, call_next):
    response = await call_next(request)
    if "text/html" in response.headers.get("content-type", "").lower():
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Exception handler for unauthenticated users (Redirect to login)
@app.exception_handler(RedirectToLoginException)
async def redirect_to_login_handler(request: Request, exc: RedirectToLoginException):
    return RedirectResponse(url="/auth/login", status_code=303)

# Exception handler for forbidden actions (Render custom 403 page)
@app.exception_handler(ForbiddenException)
async def forbidden_handler(request: Request, exc: ForbiddenException):
    return templates.TemplateResponse("errors/403.html", {"request": request}, status_code=403)

# Global exception handler for Internal Server Errors (500)
from fastapi.responses import JSONResponse
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    
    if request.url.path.startswith("/api") or request.url.path.startswith("/sales/create"):
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred."}
        )
        
    return templates.TemplateResponse(
        "errors/500.html",
        {"request": request},
        status_code=500
    )

# Create database tables and seed initial users on startup
@app.on_event("startup")
def startup_event():
    # Automatically create tables
    Base.metadata.create_all(bind=engine)
    
    # Seed default users if table is empty
    db: Session = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            print("Database is empty. Seeding default users...")
            
            # Seed Default Owner
            default_owner = User(
                full_name="Default Owner",
                email="owner@stockmate.com",
                password=hash_password("owner123"),
                role="Owner"
            )
            db.add(default_owner)
            
            # Seed Default Employee
            default_employee = User(
                full_name="Default Employee",
                email="employee@stockmate.com",
                password=hash_password("employee123"),
                role="Employee"
            )
            db.add(default_employee)
            db.commit()
            print("Successfully seeded owner (owner@stockmate.com) and employee (employee@stockmate.com).")
        
        # Seed realistic demo business data if empty
        from app.utils.seeder import seed_demo_data
        seed_demo_data(db)
    except Exception as e:
        print(f"Error during startup seeding: {e}")
        db.rollback()
    finally:
        db.close()

# Mount Static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include Routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(category.router)
app.include_router(product.router)
app.include_router(customer.router)
app.include_router(sale.router)
app.include_router(charts.router)
app.include_router(report.router)
app.include_router(export.router)
app.include_router(employee.router)
app.include_router(audit.router)
app.include_router(supplier.router)
app.include_router(purchase.router)

@app.get("/")
def read_root():
    """
    Root endpoint redirecting directly to the login screen.
    """
    return RedirectResponse(url="/auth/login", status_code=303)

@app.get("/health")
def read_health():
    """
    Health check endpoint for checking system availability.
    """
    return {"status": "healthy"}
