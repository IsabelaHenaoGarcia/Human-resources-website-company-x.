from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.core.models import CatalogMixin, TimestampMixin


class WithdrawalReason(CatalogMixin, Base):
    __tablename__ = "motivo_retiro"


class OffboardingStatus(CatalogMixin, Base):
    __tablename__ = "estado_retiro_personal"


class Offboarding(TimestampMixin, Base):
    __tablename__ = "retiro_personal"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("empleado.id"), index=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contrato.id"), index=True)
    reason_id: Mapped[int] = mapped_column(ForeignKey("motivo_retiro.id"), index=True)
    status_id: Mapped[int] = mapped_column(ForeignKey("estado_retiro_personal.id"), index=True)
    withdrawal_date: Mapped[date] = mapped_column(Date)
    observations: Mapped[str | None] = mapped_column(Text)
    exit_exam_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    equipment_returned: Mapped[bool] = mapped_column(Boolean, default=False)
    uniforms_returned: Mapped[bool] = mapped_column(Boolean, default=False)
    checklist_observations: Mapped[str | None] = mapped_column(Text)


class ContractSettlementStatus(CatalogMixin, Base):
    __tablename__ = "estado_liquidacion_contrato"


class ContractSettlement(TimestampMixin, Base):
    __tablename__ = "liquidacion_contrato"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    offboarding_id: Mapped[int] = mapped_column(ForeignKey("retiro_personal.id"), index=True)
    status_id: Mapped[int] = mapped_column(ForeignKey("estado_liquidacion_contrato.id"), index=True)
    vacation: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    bonus: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    severance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    severance_interest: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    deductions: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    observations: Mapped[str | None] = mapped_column(Text)
    approved_by_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approval_comment: Mapped[str | None] = mapped_column(Text)

