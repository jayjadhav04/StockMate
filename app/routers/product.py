import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Form, Request, HTTPException, responses
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.product import Product
from app.models.category import Category
from app.auth.dependencies import require_owner, require_employee
from app.models.user import User
from app.utils.templates import templates

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("")
def list_products(
    request: Request,
    q: Optional[str] = "",
    category_id: Optional[int] = None,
    sort_by: Optional[str] = "name",  # name, stock, cost, expiry
    sort_order: Optional[str] = "asc",  # asc, desc
    page: Optional[int] = 1,
    limit: Optional[int] = 10,
    error: Optional[str] = None,
    success: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee)
):
    """
    Lists products with searching, filtering, sorting, and pagination.
    """
    query = db.query(Product)
    
    # 1. Search
    if q:
        query = query.filter(
            or_(
                Product.product_name.like(f"%{q}%"),
                Product.description.like(f"%{q}%")
            )
        )
    
    # 2. Filter by Category
    if category_id:
        query = query.filter(Product.category_id == category_id)
        
    # 3. Sorting
    if sort_by == "stock":
        order_col = Product.stock_quantity
    elif sort_by == "cost":
        order_col = Product.cost_price
    elif sort_by == "expiry":
        order_col = Product.expiry_date
    else:  # default sorting is by product name
        order_col = Product.product_name
        
    if sort_order == "desc":
        query = query.order_by(order_col.desc())
    else:
        query = query.order_by(order_col.asc())

    # 4. Pagination
    total_count = query.count()
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()
    
    # Total pages calculation
    total_pages = (total_count + limit - 1) // limit if total_count > 0 else 1
    
    # Fetch all categories for filter dropdown
    categories = db.query(Category).order_by(Category.name.asc()).all()
    
    return templates.TemplateResponse(
        "products/list.html",
        {
            "request": request,
            "products": products,
            "categories": categories,
            "q": q,
            "category_id": category_id,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "total_count": total_count,
            "user": current_user,
            "error": error,
            "success": success
        }
    )

@router.get("/add")
def add_product_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Renders the add product form. Restricted to Owners.
    """
    categories = db.query(Category).order_by(Category.name.asc()).all()
    return templates.TemplateResponse(
        "products/form.html",
        {
            "request": request,
            "categories": categories,
            "user": current_user,
            "product": None
        }
    )

@router.post("/add")
def create_product(
    request: Request,
    product_name: str = Form(...),
    category_id: int = Form(...),
    description: Optional[str] = Form(None),
    cost_price: float = Form(...),
    stock_quantity: int = Form(...),
    minimum_stock: int = Form(...),
    gst_rate: float = Form(18.0),
    manufacturing_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Validates form data and creates a product. Restricted to Owners.
    """
    categories = db.query(Category).order_by(Category.name.asc()).all()
    errors = []

    # Basic validations
    product_name = product_name.strip()
    if not product_name:
        errors.append("Product name is required.")
    
    if cost_price <= 0:
        errors.append("Cost price must be greater than 0.")
        
    if stock_quantity < 0:
        errors.append("Stock quantity cannot be negative.")
        
    if minimum_stock < 0:
        errors.append("Minimum stock level cannot be negative.")

    # Date parsing & validation
    mfg_date = None
    exp_date = None
    
    if manufacturing_date:
        try:
            mfg_date = datetime.datetime.strptime(manufacturing_date, "%Y-%m-%d").date()
        except ValueError:
            errors.append("Invalid manufacturing date format.")
            
    if expiry_date:
        try:
            exp_date = datetime.datetime.strptime(expiry_date, "%Y-%m-%d").date()
        except ValueError:
            errors.append("Invalid expiry date format.")
            
    if mfg_date and exp_date and exp_date < mfg_date:
        errors.append("Expiry date cannot be before manufacturing date.")

    # Check duplicate product name in same category
    existing = db.query(Product).filter(
        Product.product_name == product_name,
        Product.category_id == category_id
    ).first()
    if existing:
        errors.append("A product with this name already exists in this category.")

    if errors:
        # Re-render form with validation errors and state
        form_data = {
            "product_name": product_name,
            "category_id": category_id,
            "description": description,
            "cost_price": cost_price,
            "stock_quantity": stock_quantity,
            "minimum_stock": minimum_stock,
            "manufacturing_date": manufacturing_date,
            "expiry_date": expiry_date
        }
        return templates.TemplateResponse(
            "products/form.html",
            {
                "request": request,
                "categories": categories,
                "user": current_user,
                "product": form_data,
                "error": " | ".join(errors)
            }
        )

    # Save to database
    product = Product(
        product_name=product_name,
        category_id=category_id,
        description=description,
        cost_price=cost_price,
        gst_rate=gst_rate,
        stock_quantity=stock_quantity,
        minimum_stock=minimum_stock,
        manufacturing_date=mfg_date,
        expiry_date=exp_date
    )
    db.add(product)
    db.commit()
    
    # Audit Log
    from app.utils.logger import log_action
    ip_addr = request.client.host if request.client else "127.0.0.1"
    log_action(db, current_user.id, "PRODUCT_CREATE", f"Created product '{product_name}' (ID: {product.id}, Stock: {stock_quantity})", ip_addr)
    
    return responses.RedirectResponse(url="/products?success=Product+added+successfully", status_code=303)

@router.get("/{product_id}/edit")
def edit_product_page(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Renders edit product page. Restricted to Owners.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return responses.RedirectResponse(url="/products?error=Product+not+found", status_code=303)
        
    categories = db.query(Category).order_by(Category.name.asc()).all()
    return templates.TemplateResponse(
        "products/form.html",
        {
            "request": request,
            "categories": categories,
            "user": current_user,
            "product": product
        }
    )

@router.post("/{product_id}/edit")
def edit_product(
    product_id: int,
    request: Request,
    product_name: str = Form(...),
    category_id: int = Form(...),
    description: Optional[str] = Form(None),
    cost_price: float = Form(...),
    gst_rate: float = Form(18.0),
    stock_quantity: int = Form(...),
    minimum_stock: int = Form(...),
    manufacturing_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Validates form data and updates a product. Restricted to Owners.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return responses.RedirectResponse(url="/products?error=Product+not+found", status_code=303)

    categories = db.query(Category).order_by(Category.name.asc()).all()
    errors = []

    # Validations
    product_name = product_name.strip()
    if not product_name:
        errors.append("Product name is required.")
    
    if cost_price <= 0:
        errors.append("Cost price must be greater than 0.")
        
    if stock_quantity < 0:
        errors.append("Stock quantity cannot be negative.")
        
    if minimum_stock < 0:
        errors.append("Minimum stock level cannot be negative.")

    # Date parsing & validation
    mfg_date = None
    exp_date = None
    
    if manufacturing_date:
        try:
            mfg_date = datetime.datetime.strptime(manufacturing_date, "%Y-%m-%d").date()
        except ValueError:
            errors.append("Invalid manufacturing date format.")
            
    if expiry_date:
        try:
            exp_date = datetime.datetime.strptime(expiry_date, "%Y-%m-%d").date()
        except ValueError:
            errors.append("Invalid expiry date format.")
            
    if mfg_date and exp_date and exp_date < mfg_date:
        errors.append("Expiry date cannot be before manufacturing date.")

    # Check duplicate product name in same category (excluding current product)
    existing = db.query(Product).filter(
        Product.product_name == product_name,
        Product.category_id == category_id,
        Product.id != product_id
    ).first()
    if existing:
        errors.append("A product with this name already exists in this category.")

    if errors:
        # Pass same model-like dictionary structure to retain form inputs
        form_data = {
            "id": product_id,
            "product_name": product_name,
            "category_id": category_id,
            "description": description,
            "cost_price": cost_price,
            "stock_quantity": stock_quantity,
            "minimum_stock": minimum_stock,
            "manufacturing_date": manufacturing_date,
            "expiry_date": expiry_date
        }
        return templates.TemplateResponse(
            "products/form.html",
            {
                "request": request,
                "categories": categories,
                "user": current_user,
                "product": form_data,
                "error": " | ".join(errors)
            }
        )

    # Save updates
    product.product_name = product_name
    product.category_id = category_id
    product.description = description
    product.cost_price = cost_price
    product.gst_rate = gst_rate
    product.stock_quantity = stock_quantity
    product.minimum_stock = minimum_stock
    product.manufacturing_date = mfg_date
    product.expiry_date = exp_date
    
    db.commit()
    
    # Audit Log
    from app.utils.logger import log_action
    ip_addr = request.client.host if request.client else "127.0.0.1"
    log_action(db, current_user.id, "PRODUCT_UPDATE", f"Updated product '{product_name}' (ID: {product_id})", ip_addr)
    
    return responses.RedirectResponse(url="/products?success=Product+updated+successfully", status_code=303)

@router.post("/{product_id}/delete")
def delete_product(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Deletes product. Restricted to Owners.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return responses.RedirectResponse(url="/products?error=Product+not+found", status_code=303)

    name = product.product_name
    db.delete(product)
    db.commit()
    
    # Audit Log
    from app.utils.logger import log_action
    ip_addr = request.client.host if request.client else "127.0.0.1"
    log_action(db, current_user.id, "PRODUCT_DELETE", f"Deleted product '{name}' (ID: {product_id})", ip_addr)
    
    return responses.RedirectResponse(url="/products?success=Product+deleted+successfully", status_code=303)
