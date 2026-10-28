from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from app.shared.schemas import ORMModel


class CandidateBase(BaseModel):
    document_type_id: int
    candidate_status_id: int
    full_name: str
    document_number: str
    email: str | None = None
    phone: str | None = None
    position_applied: str | None = None
    interview_result_summary: str | None = None


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(BaseModel):
    document_type_id: int | None = None
    candidate_status_id: int | None = None
    full_name: str | None = None
    document_number: str | None = None
    email: str | None = None
    phone: str | None = None
    position_applied: str | None = None
    interview_result_summary: str | None = None


class CandidateRead(CandidateBase, ORMModel):
    id: int
    references_verified: bool
    background_verified: bool
    occupational_exam_date: date | None
    occupational_exam_result: str | None
    occupational_exam_observations: str | None
    created_at: datetime
    updated_at: datetime


class VerificationCreate(BaseModel):
    referencias_verificadas: bool
    antecedentes_verificados: bool
    observaciones: str | None = None


class CandidateTestCreate(BaseModel):
    tipo_prueba: str
    resultado: str
    observaciones: str | None = None


class OccupationalExamCreate(BaseModel):
    fecha: date
    resultado: str
    observaciones: str | None = None
    documento_id: int | None = None


class InterviewCreate(BaseModel):
    candidato_id: int
    fecha_hora: datetime
    entrevistador: str
    resultado: str | None = None
    observaciones: str | None = None
    estado_entrevista_id: int


class InterviewRead(ORMModel):
    id: int
    candidate_id: int
    status_id: int
    scheduled_at: datetime
    interviewer: str
    result: str | None
    observations: str | None


class ContractCreate(BaseModel):
    empleado_id: int
    tipo_contrato_id: int
    cargo: str
    salario_base: Decimal
    fecha_inicio: date
    fecha_fin: date | None = None
    estado_contrato_id: int


class ContractRead(ORMModel):
    id: int
    employee_id: int
    contract_type_id: int
    contract_status_id: int
    position: str
    base_salary: Decimal
    start_date: date
    end_date: date | None
    created_at: datetime

