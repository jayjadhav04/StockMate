import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database import get_db
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.product import Product
from app.models.category import Category
from app.auth.dependencies import require_owner
from app.models.user import User

router = APIRouter(prefix="/api/charts", tags=["Charts API"])

@router.get("/data")
def get_chart_data(db: Session = Depends(get_db), current_user: User = Depends(require_owner)):
    """
    Retrieves aggregated dashboard chart data. Restricted to Owners.
    """
    today = datetime.date.today()
    current_year = today.year

    # 1. Daily Sales (last 7 days)
    daily_sales = []
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        start_dt = datetime.datetime.combine(day, datetime.time.min)
        end_dt = datetime.datetime.combine(day, datetime.time.max)
        amount = db.query(func.sum(Sale.total_amount)).filter(
            Sale.sale_date >= start_dt,
            Sale.sale_date <= end_dt
        ).scalar() or 0.0
        daily_sales.append({
            "date": day.strftime("%b %d"),
            "amount": float(amount)
        })

    # 2. Monthly Revenue & Profit (current year, 12 months)
    monthly_revenue = []
    monthly_profit = []
    for m in range(1, 13):
        start_dt = datetime.datetime(current_year, m, 1)
        if m == 12:
            end_dt = datetime.datetime(current_year + 1, 1, 1) - datetime.timedelta(seconds=1)
        else:
            end_dt = datetime.datetime(current_year, m + 1, 1) - datetime.timedelta(seconds=1)

        rev = db.query(func.sum(Sale.total_amount)).filter(
            Sale.sale_date >= start_dt,
            Sale.sale_date <= end_dt
        ).scalar() or 0.0
        prof = db.query(func.sum(Sale.total_profit)).filter(
            Sale.sale_date >= start_dt,
            Sale.sale_date <= end_dt
        ).scalar() or 0.0

        month_name = datetime.date(current_year, m, 1).strftime("%b")
        monthly_revenue.append({"month": month_name, "amount": float(rev)})
        monthly_profit.append({"month": month_name, "amount": float(prof)})

    # 3. Top Selling Products (limit 5)
    top_selling_raw = db.query(
        Product.product_name, 
        func.sum(SaleItem.quantity).label("total_qty")
    ).join(SaleItem, SaleItem.product_id == Product.id)\
     .group_by(Product.id)\
     .order_by(desc("total_qty"))\
     .limit(5).all()
     
    top_selling = [{"name": r[0], "quantity": int(r[1])} for r in top_selling_raw]

    # 4. Sales by Category
    cat_sales_raw = db.query(
        Category.name, 
        func.sum(SaleItem.line_total).label("total_sales")
    ).join(Product, Product.category_id == Category.id)\
     .join(SaleItem, SaleItem.product_id == Product.id)\
     .group_by(Category.id)\
     .all()
     
    category_sales = [{"category": r[0], "amount": float(r[1])} for r in cat_sales_raw]

    return {
        "daily_sales": daily_sales,
        "monthly_revenue": monthly_revenue,
        "monthly_profit": monthly_profit,
        "top_selling": top_selling,
        "category_sales": category_sales
    }
