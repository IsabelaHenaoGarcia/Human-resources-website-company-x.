from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.rbac import require_permission
from app.modules.audit.models import AuditLog
from app.modules.auth.models import User
from app.modules.audit.schemas import AuditRead
from app.shared.repository import paginate
from app.shared.schemas import PaginatedResponse

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=PaginatedResponse[AuditRead])
def list_audit(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    user_id: int | None = None,
    action: str | None = None,
    entity: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("audit:read")),
) -> dict:
    query = select(AuditLog).order_by(AuditLog.event_date.desc())
    if date_from:
        query = query.where(AuditLog.event_date >= date_from)
    if date_to:
        query = query.where(AuditLog.event_date <= date_to)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if action:
        query = query.where(AuditLog.action == action)
    if entity:
        query = query.where(AuditLog.entity == entity)
    items, total = paginate(db, query, page, page_size)
    return {"items": items, "page": page, "page_size": page_size, "total": total}
