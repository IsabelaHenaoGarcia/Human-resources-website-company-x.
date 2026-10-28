from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.audit.models import AuditLog
from app.modules.auth.models import Permission, Role, User
from app.modules.documents.models import Document, FileType
from app.modules.employees.models import Employee
from app.modules.recruitment.models import Candidate


def audit(
    db: Session,
    user: User | None,
    action: str,
    entity: str,
    record_id: int | None = None,
    detail: str | None = None,
) -> None:
    db.add(
        AuditLog(
            user_id=user.id if user else None,
            action=action,
            entity=entity,
            record_id=record_id,
            detail=detail,
        )
    )


def find_catalog_by_code(db: Session, model: type, code: str):
    return db.scalar(select(model).where(model.code == code))


def find_catalog_by_id(db: Session, model: type, item_id: int):
    item = db.get(model, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"{model.__tablename__} not found")
    return item


def ensure_unique_identity(
    db: Session,
    document_type_id: int,
    document_number: str,
    *,
    employee_id: int | None = None,
    candidate_id: int | None = None,
) -> None:
    employee_query = select(Employee).where(
        Employee.document_type_id == document_type_id,
        Employee.document_number == document_number,
    )
    if employee_id is not None:
        employee_query = employee_query.where(Employee.id != employee_id)
    if db.scalar(employee_query):
        raise HTTPException(status_code=409, detail="Duplicate identity exists in employees.")

    candidate_query = select(Candidate).where(
        Candidate.document_type_id == document_type_id,
        Candidate.document_number == document_number,
    )
    if candidate_id is not None:
        candidate_query = candidate_query.where(Candidate.id != candidate_id)
    if db.scalar(candidate_query):
        raise HTTPException(status_code=409, detail="Duplicate identity exists in candidates.")


def user_roles(user: User) -> list[str]:
    return [role.code for role in user.roles]


def user_permissions(user: User) -> list[str]:
    permissions: set[str] = set()
    for role in user.roles:
        permissions.update(permission.code for permission in role.permissions)
    return sorted(permissions)


def build_user_read(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "roles": user_roles(user),
        "permissions": user_permissions(user),
    }


def create_generated_document(
    db: Session,
    *,
    original_filename: str,
    content: bytes,
    extension: str,
    mime_type: str,
    user: User | None,
) -> Document:
    storage_root = Path(settings.storage_path)
    day_path = datetime.now(UTC).strftime("%Y/%m/%d")
    target_dir = storage_root / "generated" / day_path
    target_dir.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{uuid4().hex}.{extension}"
    target_path = target_dir / stored_filename
    target_path.write_bytes(content)

    file_type = find_catalog_by_code(db, FileType, extension)
    if file_type is None:
        file_type = FileType(code=extension, name=extension.upper(), active=True)
        db.add(file_type)
        db.flush()

    document = Document(
        file_type_id=file_type.id,
        uploaded_by_id=user.id if user else None,
        original_filename=original_filename,
        stored_filename=stored_filename,
        storage_path=str(target_path),
        mime_type=mime_type,
        file_size=len(content),
        generated=True,
    )
    db.add(document)
    db.flush()
    return document


def money(value: Decimal | int | float | None) -> Decimal:
    return Decimal(value or 0).quantize(Decimal("0.01"))
