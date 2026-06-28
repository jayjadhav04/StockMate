import datetime
import io
from typing import Optional
from fastapi import APIRouter, Depends, Request, responses
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.auth.dependencies import require_owner
from app.models.user import User
from app.utils.templates import templates
from app.utils.csv_exporter import export_sales_csv

router = APIRouter(prefix="/reports", tags=["Reports"])

def get_report_date_range(preset: str, start_date_str: Optional[str] = None, end_date_str: Optional[str] = None):
    """
    Helper to calculate datetime start/end ranges based on a preset or custom input.
    """
    today = datetime.date.today()
    start_dt = datetime.datetime.combine(today, datetime.time.min)
    end_dt = datetime.datetime.combine(today, datetime.time.max)

    if preset == "yesterday":
        yesterday = today - datetime.timedelta(days=1)
        start_dt = datetime.datetime.combine(yesterday, datetime.time.min)
        end_dt = datetime.datetime.combine(yesterday, datetime.time.max)
    elif preset == "week":
        week_ago = today - datetime.timedelta(days=6)
        start_dt = datetime.datetime.combine(week_ago, datetime.time.min)
        end_dt = datetime.datetime.combine(today, datetime.time.max)
    elif preset == "month":
        month_ago = today - datetime.timedelta(days=29)
        start_dt = datetime.datetime.combine(month_ago, datetime.time.min)
        end_dt = datetime.datetime.combine(today, datetime.time.max)
    elif preset == "year":
        start_dt = datetime.datetime(today.year, 1, 1)
        end_dt = datetime.datetime.combine(today, datetime.time.max)
    elif preset == "custom" and start_date_str and end_date_str:
        try:
            start_parsed = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_parsed = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
            start_dt = datetime.datetime.combine(start_parsed, datetime.time.min)
            end_dt = datetime.datetime.combine(end_parsed, datetime.time.max)
        except ValueError:
            pass

    return start_dt, end_dt

@router.get("")
def view_reports(
    request: Request,
    preset: Optional[str] = "today",
    start_date: Optional[str] = "",
    end_date: Optional[str] = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Renders reports filters and totals. Restricted to Owners.
    """
    start_dt, end_dt = get_report_date_range(preset, start_date, end_date)

    # 1. Fetch matching sales
    sales = db.query(Sale).filter(
        Sale.sale_date >= start_dt,
        Sale.sale_date <= end_dt
    ).order_by(Sale.sale_date.desc()).all()

    # 2. Calculate Aggregations
    revenue = db.query(func.sum(Sale.total_amount)).filter(
        Sale.sale_date >= start_dt,
        Sale.sale_date <= end_dt
    ).scalar() or 0.0

    profit = db.query(func.sum(Sale.total_profit)).filter(
        Sale.sale_date >= start_dt,
        Sale.sale_date <= end_dt
    ).scalar() or 0.0

    total_gst = db.query(func.sum(Sale.total_gst)).filter(
        Sale.sale_date >= start_dt,
        Sale.sale_date <= end_dt
    ).scalar() or 0.0

    # Total products sold
    products_sold = db.query(func.sum(SaleItem.quantity)).join(Sale, SaleItem.sale_id == Sale.id).filter(
        Sale.sale_date >= start_dt,
        Sale.sale_date <= end_dt
    ).scalar() or 0

    # Total unique customers
    customer_count = db.query(func.count(func.distinct(Sale.customer_id))).filter(
        Sale.sale_date >= start_dt,
        Sale.sale_date <= end_dt
    ).scalar() or 0

    # Product-wise profit breakdown
    from app.models.product import Product
    product_profit_rows = (
        db.query(
            Product.product_name,
            func.sum(SaleItem.quantity).label("units_sold"),
            func.sum(SaleItem.line_total).label("revenue"),
            func.sum(SaleItem.line_profit).label("profit")
        )
        .join(SaleItem, SaleItem.product_id == Product.id)
        .join(Sale, SaleItem.sale_id == Sale.id)
        .filter(Sale.sale_date >= start_dt, Sale.sale_date <= end_dt)
        .group_by(Product.id, Product.product_name)
        .order_by(func.sum(SaleItem.line_profit).desc())
        .all()
    )

    # Build list with margin % for template
    product_profit_data = []
    for row in product_profit_rows:
        rev = float(row.revenue or 0)
        pro = float(row.profit or 0)
        margin = round((pro / rev * 100), 1) if rev > 0 else 0.0
        product_profit_data.append({
            "product_name": row.product_name,
            "units_sold": int(row.units_sold or 0),
            "revenue": rev,
            "profit": pro,
            "margin": margin
        })

    return templates.TemplateResponse(
        "reports/view.html",
        {
            "request": request,
            "user": current_user,
            "sales": sales,
            "preset": preset,
            "start_date": start_date,
            "end_date": end_date,
            "revenue": float(revenue),
            "profit": float(profit),
            "total_gst": float(total_gst),
            "products_sold": int(products_sold),
            "customer_count": int(customer_count),
            "product_profit_data": product_profit_data
        }
    )

@router.get("/export")
def export_report_csv(
    preset: Optional[str] = "today",
    start_date: Optional[str] = "",
    end_date: Optional[str] = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Generates and returns a CSV file of the filtered report. Restricted to Owners.
    """
    start_dt, end_dt = get_report_date_range(preset, start_date, end_date)

    sales = db.query(Sale).filter(
        Sale.sale_date >= start_dt,
        Sale.sale_date <= end_dt
    ).order_by(Sale.sale_date.desc()).all()

    stream = io.StringIO()
    export_sales_csv(sales, stream, show_profit=True)
    
    response = responses.StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv"
    )
    
    filename = f"sales_report_{preset}_{start_dt.strftime('%Y%m%d')}_to_{end_dt.strftime('%Y%m%d')}.csv"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    
    return response
