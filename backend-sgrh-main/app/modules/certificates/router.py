from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.rbac import require_any_permission, require_permission
from app.modules.auth.models import User
from app.modules.certificates.models import CertificateStatus, EmploymentCertificate
from app.modules.employees.models import Employee
from app.modules.certificates.schemas import CertificateCreate, CertificateRead
from app.modules.documents.schemas import DocumentRead
from app.services import audit, create_generated_document

router = APIRouter(prefix="/certificates", tags=["certificates"])


def _status_id(db: Session, code: str) -> int:
    status = db.scalar(select(CertificateStatus).where(CertificateStatus.code == code))
    if status is None:
        raise HTTPException(status_code=500, detail="Certificate status catalog missing.")
    return status.id


@router.get("", response_model=list[CertificateRead])
def list_certificates(
    db: Session = Depends(get_db),
    _: User = Depends(require_any_permission("certificates:read", "reports:read")),
) -> list[EmploymentCertificate]:
    return list(db.scalars(select(EmploymentCertificate).order_by(EmploymentCertificate.created_at.desc())).all())


@router.post("", response_model=CertificateRead, status_code=201)
def create_certificate(
    payload: CertificateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("certificates:write")),
) -> EmploymentCertificate:
    if db.get(Employee, payload.empleado_id) is None:
        raise HTTPException(status_code=404, detail="Employee not found.")
    certificate = EmploymentCertificate(
        employee_id=payload.empleado_id,
        certificate_type_id=payload.tipo_certificacion_id,
        status_id=payload.estado_certificacion_id,
        observation=payload.observacion,
    )
    db.add(certificate)
    db.flush()
    audit(db, current_user, "create", "certificacion_laboral", certificate.id)
    db.commit()
    db.refresh(certificate)
    return certificate


@router.post("/{certificate_id}/generate", response_model=DocumentRead, status_code=201)
def generate_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("certificates:write")),
):
    certificate = db.get(EmploymentCertificate, certificate_id)
    if certificate is None:
        raise HTTPException(status_code=404, detail="Certificate not found.")
    employee = db.get(Employee, certificate.employee_id)
    content = (
        f"%PDF-1.4\nSGRH EMPLOYMENT CERTIFICATE STUB\nCompany: {settings.company_name}\n"
        f"Employee: {employee.full_name}\nDocument: {employee.document_number}\nPosition: {employee.position}\n"
        f"Hire date: {employee.hire_date}\nGenerated: {datetime.now(UTC).isoformat()}\nReference: {certificate.id}\n%%EOF\n"
    ).encode("utf-8")
    document = create_generated_document(
        db,
        original_filename=f"employment-certificate-{certificate.id}.pdf",
        content=content,
        extension="pdf",
        mime_type="application/pdf",
        user=current_user,
    )
    certificate.document_id = document.id
    certificate.status_id = _status_id(db, "generated")
    audit(db, current_user, "generate_certificate", "certificacion_laboral", certificate.id)
    db.commit()
    db.refresh(document)
    return document
