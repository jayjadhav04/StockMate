import datetime
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.auth.dependencies import require_owner, require_employee
from app.models.user import User
from app.models.product import Product
from app.models.customer import Customer
from app.models.sale import Sale
from app.utils.templates import templates

router = APIRouter(tags=["Dashboards"])

from fastapi.responses import RedirectResponse
from app.auth.dependencies import get_current_user

@router.get("/dashboard")
def get_dashboard_root(current_user: User = Depends(get_current_user)):
    """
    Common entry point for dashboard, redirecting based on user role.
    """
    if current_user.role == "Owner":
        return RedirectResponse(url="/owner/dashboard", status_code=303)
    return RedirectResponse(url="/employee/dashboard", status_code=303)


@router.get("/owner/dashboard")
def get_owner_dashboard(
    request: Request, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_owner)
):
    """
    Owner dashboard landing page. Calculates total business metrics, low stock counts,
    expiry counts, and lists the 5 most recent sales.
    """
    today = datetime.date.today()

    # Calculate statistics
    total_products = db.query(Product).count()
    total_customers = db.query(Customer).count()
    total_sales = db.query(Sale).count()

    revenue = db.query(func.sum(Sale.total_amount)).scalar() or 0.0
    profit = db.query(func.sum(Sale.total_profit)).scalar() or 0.0

    # Sum(cost_price * stock_quantity)
    inventory_val = db.query(func.sum(Product.cost_price * Product.stock_quantity)).scalar() or 0.0

    # Low Stock Products count
    low_stock_count = db.query(Product).filter(Product.stock_quantity < Product.minimum_stock).count()

    # Expiring products (expired or expiring in next 30 days)
    expiring_count = db.query(Product).filter(
        Product.expiry_date != None,
        Product.expiry_date <= today + datetime.timedelta(days=30)
    ).count()

    # Fetch recent 5 sales
    recent_sales = db.query(Sale).order_by(Sale.sale_date.desc()).limit(5).all()

    return templates.TemplateResponse(
        "owner_dashboard.html", 
        {
            "request": request, 
            "user": current_user,
            "total_products": total_products,
            "total_customers": total_customers,
            "total_sales": total_sales,
            "revenue": float(revenue),
            "profit": float(profit),
            "inventory_value": float(inventory_val),
            "low_stock_count": low_stock_count,
            "expiring_count": expiring_count,
            "recent_sales": recent_sales
        }
    )

@router.get("/employee/dashboard")
def get_employee_dashboard(
    request: Request, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_employee)
):
    """
    Employee dashboard landing page. Displays personal stats for the current day
    and lists the employee's 5 most recent sales.
    """
    today = datetime.date.today()
    start_dt = datetime.datetime.combine(today, datetime.time.min)
    end_dt = datetime.datetime.combine(today, datetime.time.max)

    total_products = db.query(Product).count()
    total_customers = db.query(Customer).count()

    # Today's personal sales amount sum
    personal_today_sales = db.query(func.sum(Sale.total_amount)).filter(
        Sale.employee_id == current_user.id,
        Sale.sale_date >= start_dt,
        Sale.sale_date <= end_dt
    ).scalar() or 0.0

    # Fetch recent 5 personal sales
    recent_bills = db.query(Sale).filter(
        Sale.employee_id == current_user.id
    ).order_by(Sale.sale_date.desc()).limit(5).all()

    return templates.TemplateResponse(
        "employee_dashboard.html", 
        {
            "request": request, 
            "user": current_user,
            "total_products": total_products,
            "total_customers": total_customers,
            "personal_today_sales": float(personal_today_sales),
            "recent_bills": recent_bills
        }
    )
