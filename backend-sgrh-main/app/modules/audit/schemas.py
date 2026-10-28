from datetime import datetime

from app.shared.schemas import ORMModel


class AuditRead(ORMModel):
    id: int
    user_id: int | None
    entity: str
    record_id: int | None
    action: str
    event_date: datetime
    detail: str | None

