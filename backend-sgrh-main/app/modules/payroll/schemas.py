from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from app.shared.schemas import ORMModel


class PayrollPeriodCreate(BaseModel):
    name: str
    start_date: date
    end_date: date
    status_id: int


class PayrollPeriodRead(ORMModel):
    id: int
    name: str
    start_date: date
    end_date: date
    status_id: int
    approved_by_id: int | None
    approved_at: datetime | None
    approval_comment: str | None
    created_at: datetime


class PayrollNoveltyCreate(BaseModel):
    empleado_id: int
    tipo_novedad_codigo: str
    fecha_aplicacion: date
    valor: Decimal = Decimal("0")
    cantidad_horas: Decimal | None = None
    observaciones: str | None = None
    documento_id: int | None = None


class PayrollNoveltyRead(ORMModel):
    id: int
    employee_id: int
    payroll_period_id: int
    novelty_type_id: int
    application_date: date
    amount: Decimal
    hours: Decimal | None
    observations: str | None


class ApprovalRequest(BaseModel):
    observacion: str | None = None
    aprobado_por_gerencia: bool | None = None
    aprobado_por: int | None = None


class PayrollSettlementRead(ORMModel):
    id: int
    employee_id: int
    payroll_period_id: int
    status_id: int
    base_salary: Decimal
    earnings_total: Decimal
    deductions_total: Decimal
    net_pay: Decimal
    approved_by_id: int | None
    approved_at: datetime | None
    approval_comment: str | None
    created_at: datetime

