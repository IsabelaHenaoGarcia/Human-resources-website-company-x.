from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.shared.schemas import ORMModel


class EvaluationCreate(BaseModel):
    empleado_id: int
    estado_evaluacion_id: int
    tipo_evaluacion: str
    fecha_evaluacion: date
    puntaje: Decimal | None = None
    observaciones: str | None = None


class ImprovementPlanCreate(BaseModel):
    estado_plan_mejora_id: int
    compromisos: str
    fecha_limite: date | None = None


class EvaluationRead(ORMModel):
    id: int
    employee_id: int
    status_id: int
    evaluation_type: str
    evaluation_date: date
    score: Decimal | None
    observations: str | None

