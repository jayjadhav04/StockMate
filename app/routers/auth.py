from fastapi import APIRouter, Depends, Form, Request, responses
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth.security import verify_password, create_access_token, decode_access_token
from app.utils.templates import templates

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/login")
def get_login_page(request: Request):
    """
    Renders the login page and clears any existing session cookie to enforce compulsory authentication.
    """
    response = templates.TemplateResponse("login.html", {"request": request})
    response.delete_cookie("access_token")
    return response

@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Processes login form submission, authenticates credentials, and sets session cookie.
    """
    user = db.query(User).filter(User.email == email).first()
    
    # Check if user exists and password matches
    if not user or not verify_password(password, user.password):
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Invalid email or password"}
        )
    
    # Generate JWT token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    
    # Log login action
    from app.utils.logger import log_action
    ip_addr = request.client.host if request.client else "127.0.0.1"
    log_action(db, user.id, "USER_LOGIN", f"User {user.email} successfully logged in as {user.role}.", ip_addr)
    
    # Redirect based on role
    redirect_url = "/owner/dashboard" if user.role == "Owner" else "/employee/dashboard"
    response = responses.RedirectResponse(url=redirect_url, status_code=303)
    
    # Set JWT in HttpOnly secure cookie (treated as session cookie, expires when browser closes)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    return response

@router.get("/logout")
def logout(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Logs out the user by clearing the access token cookie.
    """
    from app.auth.dependencies import require_employee
    from app.utils.logger import log_action
    
    # Retrieve current user optionally so we don't break if cookie is already missing
    ip_addr = request.client.host if request.client else "127.0.0.1"
    try:
        current_user = require_employee(request, db)
        log_action(db, current_user.id, "USER_LOGOUT", f"User {current_user.email} logged out.", ip_addr)
    except Exception:
        pass
        
    response = responses.RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response
