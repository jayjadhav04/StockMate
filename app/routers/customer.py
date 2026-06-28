from typing import Optional
from fastapi import APIRouter, Depends, Form, Request, responses
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.customer import Customer
from app.auth.dependencies import require_owner, require_employee
from app.models.user import User
from app.utils.templates import templates

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("")
def list_customers(
    request: Request,
    q: Optional[str] = "",
    error: Optional[str] = None,
    success: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee)
):
    """
    Lists customers with searching by name, phone, or email.
    """
    query = db.query(Customer)
    if q:
        query = query.filter(
            or_(
                Customer.customer_name.like(f"%{q}%"),
                Customer.phone.like(f"%{q}%"),
                Customer.email.like(f"%{q}%")
            )
        )
    
    customers = query.order_by(Customer.customer_name.asc()).all()
    
    return templates.TemplateResponse(
        "customers/list.html",
        {
            "request": request,
            "customers": customers,
            "q": q,
            "user": current_user,
            "error": error,
            "success": success
        }
    )

@router.post("")
def create_customer(
    request: Request,
    customer_name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    address: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee)
):
    """
    Creates a new customer. Accessible to both Employees and Owners.
    """
    customer_name = customer_name.strip()
    phone = phone.strip()
    email = email.strip()
    address = address.strip()

    if not customer_name or not phone or not email or not address:
        return responses.RedirectResponse(url="/customers?error=All+fields+are+required", status_code=303)

    # Simple email validation check (handled by frontend as well)
    if "@" not in email:
        return responses.RedirectResponse(url="/customers?error=Invalid+email+format", status_code=303)

    new_cust = Customer(
        customer_name=customer_name,
        phone=phone,
        email=email,
        address=address
    )
    db.add(new_cust)
    db.commit()
    
    # Audit Log
    from app.utils.logger import log_action
    ip_addr = request.client.host if request.client else "127.0.0.1"
    log_action(db, current_user.id, "CUSTOMER_CREATE", f"Created customer '{customer_name}' (ID: {new_cust.id})", ip_addr)

    return responses.RedirectResponse(url="/customers?success=Customer+added+successfully", status_code=303)

@router.post("/{customer_id}/edit")
def edit_customer(
    customer_id: int,
    request: Request,
    customer_name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    address: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee)
):
    """
    Edits customer details. Accessible to both Employees and Owners.
    """
    customer_name = customer_name.strip()
    phone = phone.strip()
    email = email.strip()
    address = address.strip()

    if not customer_name or not phone or not email or not address:
        return responses.RedirectResponse(url="/customers?error=All+fields+are+required", status_code=303)

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return responses.RedirectResponse(url="/customers?error=Customer+not+found", status_code=303)

    customer.customer_name = customer_name
    customer.phone = phone
    customer.email = email
    customer.address = address
    
    db.commit()
    
    # Audit Log
    from app.utils.logger import log_action
    ip_addr = request.client.host if request.client else "127.0.0.1"
    log_action(db, current_user.id, "CUSTOMER_UPDATE", f"Updated customer '{customer_name}' (ID: {customer_id})", ip_addr)

    return responses.RedirectResponse(url="/customers?success=Customer+updated+successfully", status_code=303)

@router.post("/{customer_id}/delete")
def delete_customer(
    customer_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Deletes customer. Restricted to Owners only.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return responses.RedirectResponse(url="/customers?error=Customer+not+found", status_code=303)

    name = customer.customer_name
    db.delete(customer)
    db.commit()
    
    # Audit Log
    from app.utils.logger import log_action
    ip_addr = request.client.host if request.client else "127.0.0.1"
    log_action(db, current_user.id, "CUSTOMER_DELETE", f"Deleted customer '{name}' (ID: {customer_id})", ip_addr)

    return responses.RedirectResponse(url="/customers?success=Customer+deleted+successfully", status_code=303)
