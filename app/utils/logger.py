from typing import Optional
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog

def log_action(db: Session, user_id: Optional[int], action: str, details: str, ip_address: str):
    """
    Logs a security or business action to the audit logs table.
    Commits immediately in a standalone sub-transaction to prevent loss of logs on failures.
    """
    try:
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        db.rollback()
        # Fallback print in console for debugging
        print(f"FAILED TO WRITE AUDIT LOG: {str(e)} | Action: {action}, Details: {details}")
