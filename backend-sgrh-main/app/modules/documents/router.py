from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.rbac import require_any_permission
from app.modules.affiliations.models import Affiliation
from app.modules.auth.models import User
from app.modules.documents.models import (
    AffiliationDocument,
    CandidateDocument,
    ContractDocument,
    Document,
    EmployeeDocument,
    FileType,
    OffboardingDocument,
    SupportDocumentType,
)
from app.modules.employees.models import Employee
from app.modules.offboarding.models import Offboarding
from app.modules.recruitment.models import Candidate, Contract
from app.modules.documents.schemas import DocumentLinkCreate, DocumentRead
from app.services import audit

router = APIRouter(tags=["documents"])


def _extension(filename: str) -> str:
    return Path(filename).suffix.lower().lstrip(".")


def _file_type(db: Session, extension: str) -> FileType:
    file_type = db.scalar(select(FileType).where(FileType.code == extension))
    if file_type is None:
        raise HTTPException(status_code=400, detail="Unsupported file type catalog value.")
    return file_type


def _ensure_exists(db: Session, model: type, object_id: int) -> None:
    if db.get(model, object_id) is None:
        raise HTTPException(status_code=404, detail=f"{model.__tablename__} not found.")


@router.post("/documents/upload", response_model=DocumentRead, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    tipo_archivo_id: int | None = None,
    nombre_archivo: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_permission("documents:write", "payroll:write", "certificates:write")),
) -> Document:
    extension = _extension(file.filename or "")
    if extension not in settings.allowed_upload_extensions:
        raise HTTPException(status_code=400, detail="Only pdf, jpg, jpeg, and png files are allowed.")
    content = await file.read()
    if len(content) > settings.upload_max_bytes:
        raise HTTPException(status_code=400, detail="File exceeds the 10 MB MVP limit.")

    file_type = db.get(FileType, tipo_archivo_id) if tipo_archivo_id else _file_type(db, extension)
    if file_type is None or file_type.code not in settings.allowed_upload_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    target_dir = Path(settings.storage_path) / "uploads"
    target_dir.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{uuid4().hex}.{extension}"
    target_path = target_dir / stored_filename
    target_path.write_bytes(content)
    document = Document(
        file_type_id=file_type.id,
        uploaded_by_id=current_user.id,
        original_filename=nombre_archivo or file.filename or stored_filename,
        stored_filename=stored_filename,
        storage_path=str(target_path),
        mime_type=file.content_type,
        file_size=len(content),
        generated=False,
    )
    db.add(document)
    db.flush()
    audit(db, current_user, "upload", "documento", document.id)
    db.commit()
    db.refresh(document)
    return document


@router.get("/documents/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_any_permission("documents:read", "payroll:read", "reports:read")),
) -> FileResponse:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    path = Path(document.storage_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Stored file not found.")
    return FileResponse(path, media_type=document.mime_type, filename=document.original_filename)


def _link_document(
    db: Session,
    current_user: User,
    payload: DocumentLinkCreate,
    model: type,
    field: str,
    entity_id: int,
) -> dict:
    _ensure_exists(db, Document, payload.document_id)
    _ensure_exists(db, SupportDocumentType, payload.support_document_type_id)
    _ensure_exists(db, model, entity_id)
    link = {
        "document_id": payload.document_id,
        "support_document_type_id": payload.support_document_type_id,
        "observation": payload.observation,
        field: entity_id,
    }
    bridge_model = {
        "employee_id": EmployeeDocument,
        "candidate_id": CandidateDocument,
        "contract_id": ContractDocument,
        "affiliation_id": AffiliationDocument,
        "offboarding_id": OffboardingDocument,
    }[field]
    row = bridge_model(**link)
    db.add(row)
    db.flush()
    audit(db, current_user, "link_document", bridge_model.__tablename__, row.id)
    db.commit()
    return {"id": row.id, **link}


@router.post("/employees/{employee_id}/documents", status_code=201)
def link_employee_document(
    employee_id: int,
    payload: DocumentLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_permission("employees:write", "documents:write")),
) -> dict:
    return _link_document(db, current_user, payload, Employee, "employee_id", employee_id)


@router.post("/candidates/{candidate_id}/documents", status_code=201)
def link_candidate_document(
    candidate_id: int,
    payload: DocumentLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_permission("recruitment:write", "documents:write")),
) -> dict:
    return _link_document(db, current_user, payload, Candidate, "candidate_id", candidate_id)


@router.post("/contracts/{contract_id}/documents", status_code=201)
def link_contract_document(
    contract_id: int,
    payload: DocumentLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_permission("recruitment:write", "documents:write")),
) -> dict:
    return _link_document(db, current_user, payload, Contract, "contract_id", contract_id)


@router.post("/affiliations/{affiliation_id}/documents", status_code=201)
def link_affiliation_document(
    affiliation_id: int,
    payload: DocumentLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_permission("affiliations:write", "documents:write")),
) -> dict:
    return _link_document(db, current_user, payload, Affiliation, "affiliation_id", affiliation_id)


@router.post("/offboarding/{offboarding_id}/documents", status_code=201)
def link_offboarding_document(
    offboarding_id: int,
    payload: DocumentLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_permission("offboarding:write", "documents:write")),
) -> dict:
    return _link_document(db, current_user, payload, Offboarding, "offboarding_id", offboarding_id)
