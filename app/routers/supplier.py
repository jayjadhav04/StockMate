from typing import Optional
from fastapi import APIRouter, Depends, Form, Request, responses
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.supplier import Supplier
from app.models.user import User
from app.auth.dependencies import require_employee, require_owner
from app.utils.templates import templates
from app.utils.logger import log_action

router = APIRouter(prefix="/suppliers", tags=["Supplier Management"])

@router.get("")
def list_suppliers(
    request: Request,
    error: Optional[str] = None,
    success: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee)
):
    """
    Lists all suppliers in the system. Accessible by both Owners and Employees.
    """
    suppliers = db.query(Supplier).order_by(Supplier.supplier_name.asc()).all()
    
    return templates.TemplateResponse(
        "suppliers/list.html",
        {
            "request": request,
            "suppliers": suppliers,
            "user": current_user,
            "error": error,
            "success": success
        }
    )

@router.post("")
def create_supplier(
    request: Request,
    supplier_name: str = Form(...),
    contact_name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Registers a new supplier. Restricted to Owners.
    """
    supplier_name = supplier_name.strip()
    if not supplier_name:
        return responses.RedirectResponse(url="/suppliers?error=Supplier+name+is+required", status_code=303)

    new_supplier = Supplier(
        supplier_name=supplier_name,
        contact_name=contact_name.strip() if contact_name else None,
        phone=phone.strip() if phone else None,
        email=email.strip().lower() if email else None,
        address=address.strip() if address else None
    )
    db.add(new_supplier)
    db.commit()

    # Log action
    ip_addr = request.client.host if request.client else "127.0.0.1"
    log_action(
        db, 
        current_user.id, 
        "SUPPLIER_CREATE", 
        f"Registered new supplier '{supplier_name}'", 
        ip_addr
    )

    return responses.RedirectResponse(url="/suppliers?success=Supplier+registered+successfully", status_code=303)

@router.post("/{supplier_id}/edit")
def edit_supplier(
    supplier_id: int,
    request: Request,
    supplier_name: str = Form(...),
    contact_name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Updates supplier details. Restricted to Owners.
    """
    supplier_name = supplier_name.strip()
    if not supplier_name:
        return responses.RedirectResponse(url="/suppliers?error=Supplier+name+is+required", status_code=303)

    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        return responses.RedirectResponse(url="/suppliers?error=Supplier+not+found", status_code=303)

    old_details = f"Name: {supplier.supplier_name}, Contact: {supplier.contact_name}, Phone: {supplier.phone}"
    
    supplier.supplier_name = supplier_name
    supplier.contact_name = contact_name.strip() if contact_name else None
    supplier.phone = phone.strip() if phone else None
    supplier.email = email.strip().lower() if email else None
    supplier.address = address.strip() if address else None
    
    db.commit()

    # Log action
    ip_addr = request.client.host if request.client else "127.0.0.1"
    log_action(
        db, 
        current_user.id, 
        "SUPPLIER_UPDATE", 
        f"Updated supplier ID {supplier_id} (Old: {old_details} | New: Name: {supplier_name}, Contact: {contact_name})", 
        ip_addr
    )

    return responses.RedirectResponse(url="/suppliers?success=Supplier+updated+successfully", status_code=303)

@router.post("/{supplier_id}/delete")
def delete_supplier(
    supplier_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Deletes supplier profile. Restricted to Owners.
    """
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        return responses.RedirectResponse(url="/suppliers?error=Supplier+not+found", status_code=303)

    name = supplier.supplier_name
    db.delete(supplier)
    db.commit()

    # Log action
    ip_addr = request.client.host if request.client else "127.0.0.1"
    log_action(
        db, 
        current_user.id, 
        "SUPPLIER_DELETE", 
        f"Deleted supplier '{name}' (ID: {supplier_id})", 
        ip_addr
    )

    return responses.RedirectResponse(url="/suppliers?success=Supplier+deleted+successfully", status_code=303)
