import math
from typing import Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.auth.dependencies import require_owner
from app.utils.templates import templates

router = APIRouter(prefix="/audit-logs", tags=["Security Audit Logs"])

ACTIONS_LIST = [
    "USER_LOGIN", "USER_LOGOUT",
    "PRODUCT_CREATE", "PRODUCT_UPDATE", "PRODUCT_DELETE",
    "CATEGORY_CREATE", "CATEGORY_UPDATE", "CATEGORY_DELETE",
    "CUSTOMER_CREATE", "CUSTOMER_UPDATE", "CUSTOMER_DELETE",
    "INVOICE_CREATE",
    "EMPLOYEE_CREATE", "EMPLOYEE_UPDATE", "EMPLOYEE_DELETE"
]

@router.get("")
def view_audit_logs(
    request: Request,
    page: int = 1,
    action_type: Optional[str] = "",
    user_filter: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    """
    Lists paginated and filtered audit logs. Restricted to Owners.
    """
    if page < 1:
        page = 1
        
    page_size = 25
    offset = (page - 1) * page_size

    query = db.query(AuditLog)

    # Apply filters
    if action_type:
        query = query.filter(AuditLog.action == action_type)
        
    if user_filter:
        query = query.filter(AuditLog.user_id == user_filter)

    # Get count before offset/limit
    total_count = query.count()
    total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1

    logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(page_size).all()

    # Load users for filter dropdown
    users = db.query(User).order_by(User.full_name.asc()).all()

    return templates.TemplateResponse(
        "audit_logs/list.html",
        {
            "request": request,
            "logs": logs,
            "user": current_user,
            "users": users,
            "action_types": ACTIONS_LIST,
            "current_action": action_type,
            "current_user_filter": user_filter,
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_count
        }
    )
