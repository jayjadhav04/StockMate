import io
from fastapi import APIRouter, Depends, responses
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.sale import Sale
from app.auth.dependencies import require_owner
from app.models.user import User
from app.utils import csv_exporter

router = APIRouter(prefix="/exports", tags=["Data Exports"])

@router.get("/products")
def export_products(db: Session = Depends(get_db), current_user: User = Depends(require_owner)):
    """
    Downloads products catalog as CSV. Restricted to Owners.
    """
    stream = io.StringIO()
    csv_exporter.export_products_csv(db, stream)
    
    response = responses.StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=products_inventory.csv"
    return response

@router.get("/customers")
def export_customers(db: Session = Depends(get_db), current_user: User = Depends(require_owner)):
    """
    Downloads customers database as CSV. Restricted to Owners.
    """
    stream = io.StringIO()
    csv_exporter.export_customers_csv(db, stream)
    
    response = responses.StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=customers_list.csv"
    return response

@router.get("/sales")
def export_sales(db: Session = Depends(get_db), current_user: User = Depends(require_owner)):
    """
    Downloads complete sales history as CSV. Restricted to Owners.
    """
    sales = db.query(Sale).order_by(Sale.sale_date.desc()).all()
    stream = io.StringIO()
    csv_exporter.export_sales_csv(sales, stream, show_profit=True)
    
    response = responses.StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=sales_history.csv"
    return response
