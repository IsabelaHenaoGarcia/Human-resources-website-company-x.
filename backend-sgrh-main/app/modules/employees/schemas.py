from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from app.shared.schemas import ORMModel


class EmployeeBase(BaseModel):
    document_type_id: int
    employee_status_id: int
    full_name: str
    document_number: str
    birth_date: date | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    position: str
    hire_date: date
    base_salary: Decimal = Decimal("0")
    eps_entity: str | None = None
    pension_entity: str | None = None
    has_beneficiaries: bool = False
    beneficiary_notes: str | None = None
    induction_completed: bool = False
    latest_evaluation_status: str | None = None
    latest_evaluation_date: date | None = None
    user_id: int | None = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    document_type_id: int | None = None
    employee_status_id: int | None = None
    full_name: str | None = None
    document_number: str | None = None
    birth_date: date | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    position: str | None = None
    hire_date: date | None = None
    base_salary: Decimal | None = None
    eps_entity: str | None = None
    pension_entity: str | None = None
    has_beneficiaries: bool | None = None
    beneficiary_notes: str | None = None
    induction_completed: bool | None = None
    latest_evaluation_status: str | None = None
    latest_evaluation_date: date | None = None
    user_id: int | None = None


class EmployeeRead(EmployeeBase, ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime

