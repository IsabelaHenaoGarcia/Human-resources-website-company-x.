from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.core.models import CatalogMixin, TimestampMixin


class EvaluationStatus(CatalogMixin, Base):
    __tablename__ = "estado_evaluacion"


class PerformanceEvaluation(TimestampMixin, Base):
    __tablename__ = "evaluacion_desempeno"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("empleado.id"), index=True)
    status_id: Mapped[int] = mapped_column(ForeignKey("estado_evaluacion.id"), index=True)
    evaluation_type: Mapped[str] = mapped_column(String(80))
    evaluation_date: Mapped[date] = mapped_column(Date)
    score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    observations: Mapped[str | None] = mapped_column(Text)


class ImprovementPlanStatus(CatalogMixin, Base):
    __tablename__ = "estado_plan_mejora"


class ImprovementPlan(TimestampMixin, Base):
    __tablename__ = "plan_mejora"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    evaluation_id: Mapped[int] = mapped_column(ForeignKey("evaluacion_desempeno.id"), index=True)
    status_id: Mapped[int] = mapped_column(ForeignKey("estado_plan_mejora.id"), index=True)
    commitments: Mapped[str] = mapped_column(Text)
    due_date: Mapped[date | None] = mapped_column(Date)

