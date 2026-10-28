from datetime import date

from pydantic import BaseModel

from app.shared.schemas import ORMModel


class TrainingActivityCreate(BaseModel):
    type_id: int
    status_id: int
    name: str
    scheduled_date: date
    description: str | None = None


class TrainingAttendanceCreate(BaseModel):
    empleado_id: int
    asistio: bool = True
    observaciones: str | None = None


class AnnualTrainingPlanCreate(BaseModel):
    year: int
    description: str | None = None


class TrainingActivityRead(ORMModel):
    id: int
    type_id: int
    status_id: int
    name: str
    scheduled_date: date
    description: str | None

