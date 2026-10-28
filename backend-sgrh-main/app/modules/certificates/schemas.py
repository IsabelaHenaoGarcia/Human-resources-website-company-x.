from pydantic import BaseModel

from app.shared.schemas import ORMModel


class CertificateCreate(BaseModel):
    empleado_id: int
    tipo_certificacion_id: int
    observacion: str | None = None
    estado_certificacion_id: int


class CertificateRead(ORMModel):
    id: int
    employee_id: int
    certificate_type_id: int
    status_id: int
    document_id: int | None
    observation: str | None

