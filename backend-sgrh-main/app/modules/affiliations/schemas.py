from datetime import date, datetime

from pydantic import BaseModel

from app.shared.schemas import ORMModel


class AffiliationCreate(BaseModel):
    empleado_id: int
    tipo_afiliacion_id: int
    entidad: str
    fecha_registro: date
    estado_afiliacion_id: int
    observaciones: str | None = None


class AffiliationUpdate(BaseModel):
    tipo_afiliacion_id: int | None = None
    entidad: str | None = None
    fecha_registro: date | None = None
    estado_afiliacion_id: int | None = None
    observaciones: str | None = None


class AffiliationRead(ORMModel):
    id: int
    employee_id: int
    affiliation_type_id: int
    affiliation_status_id: int
    entity: str
    registration_date: date
    observations: str | None
    created_at: datetime

