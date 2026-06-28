from typing import Optional
from fastapi import APIRouter, Depends, Form, Request, HTTPException, responses
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.category import Category
from app.auth.dependencies import require_owner, require_employee
from app.models.user import User
from app.utils.templates import templates

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("")
def list_categories(
    request: Request,
    q: Optional[str] = "",
    error: Optional[str] = None,
    success: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee)
):
    """
    Renders categories list page. Search filter by name is supported.
    """
    query = db.query(Category)
    if q:
        query = query.filter(Category.name.like(f"%{q}%"))
    
    categories = query.order_by(Category.name.asc()).all()
    
    return templates.TemplateResponse(
        "categories/list.html",
        {
            "request": request,
            "categories": categories,
            "q": q,
            "user": current_user,
            "error": error,
            "success": success
        }
    )

@router.post("")
def create_category(
    request: Request,
    name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Creates a new category. Restricted to Owners.
    """
    name = name.strip()
    if not name:
        return responses.RedirectResponse(url="/categories?error=Category+name+cannot+be+empty", status_code=303)
        
    # Check duplicate
    existing = db.query(Category).filter(Category.name == name).first()
    if existing:
        return responses.RedirectResponse(url="/categories?error=Category+already+exists", status_code=303)

    new_cat = Category(name=name)
    db.add(new_cat)
    db.commit()
    
    # Audit Log
    from app.utils.logger import log_action
    ip_addr = request.client.host if request.client else "127.0.0.1"
    log_action(db, current_user.id, "CATEGORY_CREATE", f"Created category '{name}' (ID: {new_cat.id})", ip_addr)
    
    return responses.RedirectResponse(url="/categories?success=Category+added+successfully", status_code=303)

@router.post("/{category_id}/edit")
def edit_category(
    category_id: int,
    request: Request,
    name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Edits category name. Restricted to Owners.
    """
    name = name.strip()
    if not name:
        return responses.RedirectResponse(url="/categories?error=Category+name+cannot+be+empty", status_code=303)

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return responses.RedirectResponse(url="/categories?error=Category+not+found", status_code=303)

    # Check duplicate name for another category
    existing = db.query(Category).filter(Category.name == name, Category.id != category_id).first()
    if existing:
        return responses.RedirectResponse(url="/categories?error=Category+name+already+exists", status_code=303)

    old_name = category.name
    category.name = name
    db.commit()
    
    # Audit Log
    from app.utils.logger import log_action
    ip_addr = request.client.host if request.client else "127.0.0.1"
    log_action(db, current_user.id, "CATEGORY_UPDATE", f"Updated category ID {category_id} from '{old_name}' to '{name}'", ip_addr)
    
    return responses.RedirectResponse(url="/categories?success=Category+updated+successfully", status_code=303)

@router.post("/{category_id}/delete")
def delete_category(
    category_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Deletes category. Restricted to Owners.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return responses.RedirectResponse(url="/categories?error=Category+not+found", status_code=303)

    name = category.name
    db.delete(category)
    db.commit()
    
    # Audit Log
    from app.utils.logger import log_action
    ip_addr = request.client.host if request.client else "127.0.0.1"
    log_action(db, current_user.id, "CATEGORY_DELETE", f"Deleted category '{name}' (ID: {category_id})", ip_addr)
    
    return responses.RedirectResponse(url="/categories?success=Category+deleted+successfully", status_code=303)
