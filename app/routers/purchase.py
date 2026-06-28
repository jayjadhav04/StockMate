from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, responses
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.user import User
from app.schemas.purchase import PurchaseOrderCreate
from app.auth.dependencies import require_employee, require_owner
from app.utils.templates import templates
from app.utils.logger import log_action

router = APIRouter(prefix="/purchases", tags=["Purchase Orders Management"])

@router.get("")
def list_purchases(
    request: Request,
    error: Optional[str] = None,
    success: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee)
):
    """
    Lists all purchase orders in reverse chronological order.
    """
    orders = db.query(PurchaseOrder).order_by(PurchaseOrder.created_at.desc()).all()
    
    return templates.TemplateResponse(
        "purchases/list.html",
        {
            "request": request,
            "orders": orders,
            "user": current_user,
            "error": error,
            "success": success
        }
    )

@router.get("/create")
def get_create_purchase(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee)
):
    """
    Renders the interactive purchase order builder form.
    """
    suppliers = db.query(Supplier).order_by(Supplier.supplier_name.asc()).all()
    products = db.query(Product).order_by(Product.product_name.asc()).all()
    
    return templates.TemplateResponse(
        "purchases/create.html",
        {
            "request": request,
            "suppliers": suppliers,
            "products": products,
            "user": current_user
        }
    )

@router.post("/create")
def create_purchase(
    payload: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee)
):
    """
    Processes the submittal of a new purchase order draft (status: Pending).
    """
    # 1. Verify supplier
    supplier = db.query(Supplier).filter(Supplier.id == payload.supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    # 2. Verify all products exist
    product_ids = [item.product_id for item in payload.items]
    existing_products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    if len(existing_products) != len(set(product_ids)):
        raise HTTPException(status_code=400, detail="One or more selected products are invalid")

    product_map = {p.id: p for p in existing_products}

    # 3. Calculate total and build items
    total_amount = 0.0
    po_items = []

    for item in payload.items:
        line_total = item.quantity * item.cost_price
        total_amount += line_total
        
        po_item = PurchaseOrderItem(
            product_id=item.product_id,
            quantity=item.quantity,
            cost_price=item.cost_price,
            line_total=line_total
        )
        po_items.append(po_item)

    # 4. Create PO Header
    po = PurchaseOrder(
        supplier_id=payload.supplier_id,
        total_amount=total_amount,
        status="Pending"
    )
    db.add(po)
    db.flush()  # Populates po.id for items

    for po_item in po_items:
        po_item.purchase_order_id = po.id
        db.add(po_item)

    db.commit()

    return {"status": "success", "redirect": "/purchases?success=Purchase+order+draft+created+successfully"}

@router.post("/{po_id}/complete")
def complete_purchase(
    po_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Approves and completes a Purchase Order. RESTOCKS inventory and UPDATES cost prices.
    Restricted to Owners.
    """
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        return responses.RedirectResponse(url="/purchases?error=Purchase+order+not+found", status_code=303)

    if po.status == "Completed":
        return responses.RedirectResponse(url="/purchases?error=Purchase+order+is+already+completed", status_code=303)

    # Perform stock increment and cost updates
    for item in po.items:
        prod = db.query(Product).filter(Product.id == item.product_id).first()
        if prod:
            # Update cost price to the latest purchasing price
            prod.cost_price = item.cost_price
            # Replenish stock quantity
            prod.stock_quantity += item.quantity

    po.status = "Completed"
    db.commit()

    # Log action
    ip_addr = request.client.host if request.client else "127.0.0.1"
    log_action(
        db, 
        current_user.id, 
        "PURCHASE_COMPLETE", 
        f"Approved & completed Purchase Order ID {po.id} (Supplier: {po.supplier.supplier_name}, Total Cost: ${po.total_amount:.2f}). Inventory replenished.", 
        ip_addr
    )

    return responses.RedirectResponse(url="/purchases?success=Purchase+order+completed.+Stock+updated.", status_code=303)

@router.post("/{po_id}/delete")
def delete_purchase(
    po_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Deletes a Pending purchase order. Completed orders cannot be deleted.
    Restricted to Owners.
    """
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        return responses.RedirectResponse(url="/purchases?error=Purchase+order+not+found", status_code=303)

    if po.status == "Completed":
        return responses.RedirectResponse(url="/purchases?error=Cannot+delete+a+completed+purchase+order", status_code=303)

    db.delete(po)
    db.commit()

    # Log action
    ip_addr = request.client.host if request.client else "127.0.0.1"
    log_action(
        db, 
        current_user.id, 
        "PURCHASE_DELETE", 
        f"Deleted pending Purchase Order ID {po_id}", 
        ip_addr
    )

    return responses.RedirectResponse(url="/purchases?success=Purchase+order+deleted+successfully", status_code=303)
