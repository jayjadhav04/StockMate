from typing import Optional
from fastapi import APIRouter, Depends, Form, Request, responses
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth.security import hash_password
from app.auth.dependencies import require_owner
from app.utils.templates import templates
from app.utils.logger import log_action

router = APIRouter(prefix="/employees", tags=["Employee Management"])

@router.get("")
def list_employees(
    request: Request,
    error: Optional[str] = None,
    success: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Lists all users in the system. Restricted to Owners.
    """
    users = db.query(User).order_by(User.role.asc(), User.full_name.asc()).all()
    
    return templates.TemplateResponse(
        "employees/list.html",
        {
            "request": request,
            "employees": users,
            "user": current_user,
            "error": error,
            "success": success
        }
    )

@router.post("")
def create_employee(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Creates a new user account (Owner or Employee). Restricted to Owners.
    """
    full_name = full_name.strip()
    email = email.strip().lower()
    password = password.strip()
    
    if not full_name or not email or not password or not role:
        return responses.RedirectResponse(url="/employees?error=All+fields+are+required", status_code=303)

    if role not in ["Owner", "Employee"]:
        return responses.RedirectResponse(url="/employees?error=Invalid+role", status_code=303)

    # Check duplicate email
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return responses.RedirectResponse(url="/employees?error=Email+already+registered", status_code=303)

    new_user = User(
        full_name=full_name,
        email=email,
        password=hash_password(password),
        role=role
    )
    db.add(new_user)
    db.commit()

    # Log action
    ip_addr = request.client.host if request.client else "127.0.0.1"
    log_action(
        db, 
        current_user.id, 
        "EMPLOYEE_CREATE", 
        f"Registered new user '{full_name}' ({email}) as {role}", 
        ip_addr
    )

    return responses.RedirectResponse(url="/employees?success=Account+created+successfully", status_code=303)

@router.post("/{user_id}/edit")
def edit_employee(
    user_id: int,
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    password: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Updates user details. Optionally hashes password if provided. Restricted to Owners.
    """
    full_name = full_name.strip()
    email = email.strip().lower()
    
    if not full_name or not email or not role:
        return responses.RedirectResponse(url="/employees?error=All+fields+are+required", status_code=303)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return responses.RedirectResponse(url="/employees?error=User+not+found", status_code=303)

    # Check email duplicate
    existing = db.query(User).filter(User.email == email, User.id != user_id).first()
    if existing:
        return responses.RedirectResponse(url="/employees?error=Email+already+registered", status_code=303)

    old_details = f"Name: {user.full_name}, Email: {user.email}, Role: {user.role}"
    
    # Save updates
    user.full_name = full_name
    user.email = email
    user.role = role
    
    if password and password.strip():
        user.password = hash_password(password.strip())
        
    db.commit()

    # Log action
    ip_addr = request.client.host if request.client else "127.0.0.1"
    log_action(
        db, 
        current_user.id, 
        "EMPLOYEE_UPDATE", 
        f"Updated user ID {user_id} (Old: {old_details} | New: Name: {full_name}, Email: {email}, Role: {role})", 
        ip_addr
    )

    return responses.RedirectResponse(url="/employees?success=Account+updated+successfully", status_code=303)

@router.post("/{user_id}/delete")
def delete_employee(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Deletes user account. Enforces that Owners cannot delete themselves. Restricted to Owners.
    """
    # Prevent self-deletion
    if user_id == current_user.id:
        return responses.RedirectResponse(url="/employees?error=You+cannot+delete+your+own+account", status_code=303)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return responses.RedirectResponse(url="/employees?error=User+not+found", status_code=303)

    name = user.full_name
    email = user.email
    db.delete(user)
    db.commit()

    # Log action
    ip_addr = request.client.host if request.client else "127.0.0.1"
    log_action(
        db, 
        current_user.id, 
        "EMPLOYEE_DELETE", 
        f"Deleted user account '{name}' ({email}, ID: {user_id})", 
        ip_addr
    )

    return responses.RedirectResponse(url="/employees?success=Account+deleted+successfully", status_code=303)
