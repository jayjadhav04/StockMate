import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException, responses
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.product import Product
from app.models.customer import Customer
from app.auth.dependencies import require_employee
from app.models.user import User
from app.schemas.sale import SaleCreate
from app.utils.templates import templates

router = APIRouter(prefix="/sales", tags=["Sales"])

@router.get("")
def list_sales(
    request: Request,
    q: Optional[str] = "",
    date_filter: Optional[str] = "",
    error: Optional[str] = None,
    success: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee)
):
    """
    Lists sales history.
    - Owners see all sales.
    - Employees see only their personal sales.
    Supports search by invoice number or customer name, and date filtering.
    """
    query = db.query(Sale).join(Customer)
    
    # Apply Role-based filtering
    if current_user.role == "Employee":
        query = query.filter(Sale.employee_id == current_user.id)
        
    # Apply search filter
    if q:
        query = query.filter(
            or_(
                Sale.invoice_number.like(f"%{q}%"),
                Customer.customer_name.like(f"%{q}%")
            )
        )
        
    # Apply date filter
    if date_filter:
        try:
            parsed_date = datetime.datetime.strptime(date_filter, "%Y-%m-%d").date()
            query = query.filter(Sale.sale_date.like(f"%{parsed_date}%"))
        except ValueError:
            pass

    sales = query.order_by(Sale.sale_date.desc()).all()
    
    return templates.TemplateResponse(
        "sales/list.html",
        {
            "request": request,
            "sales": sales,
            "q": q,
            "date_filter": date_filter,
            "user": current_user,
            "error": error,
            "success": success
        }
    )

@router.get("/create")
def get_create_sale_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee)
):
    """
    Renders the invoice builder page.
    Loads list of products (with gst_rate) and customers.
    """
    products = db.query(Product).order_by(Product.product_name.asc()).all()
    customers = db.query(Customer).order_by(Customer.customer_name.asc()).all()
    
    return templates.TemplateResponse(
        "sales/create.html",
        {
            "request": request,
            "products": products,
            "customers": customers,
            "user": current_user
        }
    )

@router.post("/create")
def create_sale(
    request: Request,
    payload: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee)
):
    """
    Creates a sale with GST calculation per line item.
    Generates invoice numbers, calculates subtotal/GST/profit,
    verifies and decrements stock. Transactional safety via SELECT FOR UPDATE.
    """
    # 1. Fetch the customer to verify existence
    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="Selected customer not found.")

    # 2. Start checking stock and preparing sale items
    total_amount = 0.0   # Pre-GST subtotal
    total_profit = 0.0
    total_gst = 0.0
    sale_items = []
    
    # Process items inside transaction block
    try:
        # Loop through each item in the payload and query with lock (with_for_update)
        for item in payload.items:
            product = db.query(Product).filter(Product.id == item.product_id).with_for_update().first()
            if not product:
                raise HTTPException(status_code=400, detail=f"Product with ID {item.product_id} not found.")

            # Validate stock quantity
            if product.stock_quantity < item.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Insufficient stock for '{product.product_name}'. Available: {product.stock_quantity}, Requested: {item.quantity}."
                )

            # Deduct stock
            product.stock_quantity -= item.quantity
            
            # Use GST rate from payload (sent by frontend from product's gst_rate attribute)
            gst_rate = item.gst_rate if item.gst_rate is not None else product.gst_rate

            # Calculations
            line_total = item.selling_price * item.quantity          # Pre-GST amount
            gst_amount = round(line_total * gst_rate / 100, 2)       # GST for this line
            line_profit = (item.selling_price - product.cost_price) * item.quantity
            
            total_amount += line_total
            total_gst += gst_amount
            total_profit += line_profit

            # Create sale item
            sale_item = SaleItem(
                product_id=product.id,
                quantity=item.quantity,
                cost_price=product.cost_price,
                selling_price=item.selling_price,
                line_total=line_total,
                gst_amount=gst_amount,
                line_profit=line_profit
            )
            sale_items.append(sale_item)

        # 3. Generate unique sequential invoice number
        last_sale = db.query(Sale).order_by(Sale.id.desc()).first()
        next_id = 1
        if last_sale:
            try:
                num_part = last_sale.invoice_number.split("-")[1]
                next_id = int(num_part) + 1
            except Exception:
                next_id = last_sale.id + 1
        invoice_number = f"INV-{next_id:06d}"

        # 4. Save Sale Header
        sale = Sale(
            invoice_number=invoice_number,
            customer_id=payload.customer_id,
            employee_id=current_user.id,
            total_amount=round(total_amount, 2),
            total_profit=round(total_profit, 2),
            total_gst=round(total_gst, 2),
            payment_method=payload.payment_method
        )
        db.add(sale)
        db.flush()  # Populates sale.id for children

        # 5. Save Sale Items linked to header
        for s_item in sale_items:
            s_item.sale_id = sale.id
            db.add(s_item)

        # Commit transaction (updates stock levels and logs invoice)
        db.commit()
        
        # Audit Log
        from app.utils.logger import log_action
        ip_addr = request.client.host if request.client else "127.0.0.1"
        grand_total = round(total_amount + total_gst, 2)
        log_action(db, current_user.id, "INVOICE_CREATE", f"Billed invoice {invoice_number} to customer ID {payload.customer_id} (Subtotal: ₹{total_amount:.2f}, GST: ₹{total_gst:.2f}, Grand Total: ₹{grand_total:.2f}, Payment: {payload.payment_method})", ip_addr)
        
        return {"status": "success", "invoice_number": invoice_number, "redirect": "/sales?success=Invoice+created+successfully"}
        
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database transaction failed: {str(e)}")

@router.get("/{sale_id}/pdf")
def get_invoice_pdf(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee)
):
    """
    Generates and downloads the PDF invoice for the specified sale.
    PDF includes GST breakdown and payment method.
    """
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        return responses.RedirectResponse(url="/sales?error=Invoice+not+found", status_code=303)
        
    # Enforce role boundaries for personal sales
    if current_user.role == "Employee" and sale.employee_id != current_user.id:
        return responses.RedirectResponse(url="/sales?error=Unauthorized+access", status_code=303)

    import io
    from app.utils.pdf_generator import generate_invoice_pdf
    
    buffer = io.BytesIO()
    generate_invoice_pdf(sale, buffer)
    buffer.seek(0)
    
    response = responses.StreamingResponse(buffer, media_type="application/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename={sale.invoice_number}.pdf"
    return response

@router.post("/{sale_id}/delete")
def delete_sale(
    sale_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee)
):
    """
    Deletes an invoice record (Owner only). Does NOT restore stock.
    """
    from app.auth.dependencies import ForbiddenException
    if current_user.role != "Owner":
        raise ForbiddenException()
    
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        return responses.RedirectResponse(url="/sales?error=Invoice+not+found", status_code=303)
    
    invoice_number = sale.invoice_number
    db.delete(sale)
    db.commit()
    
    from app.utils.logger import log_action
    ip_addr = request.client.host if request.client else "127.0.0.1"
    log_action(db, current_user.id, "SALE_DELETE", f"Deleted invoice {invoice_number}", ip_addr)
    
    return responses.RedirectResponse(url="/sales?success=Invoice+deleted", status_code=303)
