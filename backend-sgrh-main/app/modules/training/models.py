from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.core.models import CatalogMixin, TimestampMixin


class TrainingActivityType(CatalogMixin, Base):
    __tablename__ = "tipo_actividad_formativa"


class TrainingActivityStatus(CatalogMixin, Base):
    __tablename__ = "estado_actividad_formativa"


class TrainingActivity(TimestampMixin, Base):
    __tablename__ = "actividad_formativa"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_id: Mapped[int] = mapped_column(ForeignKey("tipo_actividad_formativa.id"), index=True)
    status_id: Mapped[int] = mapped_column(ForeignKey("estado_actividad_formativa.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    scheduled_date: Mapped[date] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(Text)


class TrainingAttendance(TimestampMixin, Base):
    __tablename__ = "asistencia_actividad_formativa"
    __table_args__ = (UniqueConstraint("training_activity_id", "employee_id", name="uq_attendance_activity_employee"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    training_activity_id: Mapped[int] = mapped_column(ForeignKey("actividad_formativa.id"), index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("empleado.id"), index=True)
    attended: Mapped[bool] = mapped_column(Boolean, default=True)
    observations: Mapped[str | None] = mapped_column(Text)


class AnnualTrainingPlan(TimestampMixin, Base):
    __tablename__ = "plan_anual_capacitacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    year: Mapped[int] = mapped_column(Integer, unique=True)
    description: Mapped[str | None] = mapped_column(Text)

