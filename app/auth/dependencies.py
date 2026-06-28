from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth.security import decode_access_token

class RedirectToLoginException(Exception):
    """
    Raised when an unauthenticated user attempts to access an HTML route.
    """
    pass

class ForbiddenException(Exception):
    """
    Raised when a user attempts to access a route for which they do not have roles.
    """
    pass

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Dependency to retrieve the logged-in user from the JWT access token cookie.
    If validation fails:
      - Redirects to /auth/login for browser HTML requests.
      - Raises HTTP 401 for normal API requests.
    """
    token = request.cookies.get("access_token")
    is_html_request = "text/html" in request.headers.get("accept", "")

    if not token:
        if is_html_request:
            raise RedirectToLoginException()
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_access_token(token)
    if not payload:
        if is_html_request:
            raise RedirectToLoginException()
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        if is_html_request:
            raise RedirectToLoginException()
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        if is_html_request:
            raise RedirectToLoginException()
        raise HTTPException(status_code=401, detail="User not found")

    return user

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, request: Request, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            is_html_request = "text/html" in request.headers.get("accept", "")
            if is_html_request:
                raise ForbiddenException()
            raise HTTPException(status_code=403, detail="Role not authorized")
        return current_user

# Pre-defined dependencies for routes
require_owner = RoleChecker(["Owner"])
require_employee = RoleChecker(["Owner", "Employee"])  # Owners can also view employee dashboards
