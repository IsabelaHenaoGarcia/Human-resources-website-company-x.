from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from app.shared.schemas import ORMModel


class OffboardingCreate(BaseModel):
    empleado_id: int
    contrato_id: int
    fecha_retiro: date
    motivo_retiro_id: int
    observaciones: str | None = None
    estado_retiro_id: int


class ExitChecklistCreate(BaseModel):
    examen_retiro_realizado: bool
    implementos_entregados: bool
    dotacion_entregada: bool
    observaciones: str | None = None


class ContractSettlementCreate(BaseModel):
    vacaciones: Decimal = Decimal("0")
    prima: Decimal = Decimal("0")
    cesantias: Decimal = Decimal("0")
    intereses_cesantias: Decimal = Decimal("0")
    deducciones: Decimal = Decimal("0")
    observaciones: str | None = None
    estado_liquidacion_id: int


class OffboardingRead(ORMModel):
    id: int
    employee_id: int
    contract_id: int
    reason_id: int
    status_id: int
    withdrawal_date: date
    observations: str | None
    exit_exam_completed: bool
    equipment_returned: bool
    uniforms_returned: bool
    checklist_observations: str | None


class ContractSettlementRead(ORMModel):
    id: int
    offboarding_id: int
    status_id: int
    vacation: Decimal
    bonus: Decimal
    severance: Decimal
    severance_interest: Decimal
    deductions: Decimal
    total: Decimal
    observations: str | None
    approved_by_id: int | None
    approved_at: datetime | None
    approval_comment: str | None

