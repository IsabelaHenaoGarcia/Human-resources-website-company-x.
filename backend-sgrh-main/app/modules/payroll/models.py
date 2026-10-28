from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.core.models import CatalogMixin, TimestampMixin


class PayrollPeriodStatus(CatalogMixin, Base):
    __tablename__ = "estado_periodo_nomina"


class PayrollPeriod(TimestampMixin, Base):
    __tablename__ = "periodo_nomina"
    __table_args__ = (UniqueConstraint("start_date", "end_date", name="uq_payroll_period_dates"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status_id: Mapped[int] = mapped_column(ForeignKey("estado_periodo_nomina.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    approved_by_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approval_comment: Mapped[str | None] = mapped_column(Text)

    status: Mapped[PayrollPeriodStatus] = relationship()


class PayrollNoveltyType(CatalogMixin, Base):
    __tablename__ = "tipo_novedad_nomina"

    calculation_effect: Mapped[str] = mapped_column(String(40))


class PayrollNovelty(TimestampMixin, Base):
    __tablename__ = "novedad_nomina"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("empleado.id"), index=True)
    payroll_period_id: Mapped[int] = mapped_column(ForeignKey("periodo_nomina.id"), index=True)
    novelty_type_id: Mapped[int] = mapped_column(ForeignKey("tipo_novedad_nomina.id"), index=True)
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documento.id"), nullable=True)
    application_date: Mapped[date] = mapped_column(Date)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    hours: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    observations: Mapped[str | None] = mapped_column(Text)

    employee: Mapped["Employee"] = relationship()
    period: Mapped[PayrollPeriod] = relationship()
    novelty_type: Mapped[PayrollNoveltyType] = relationship()


class PayrollSettlementStatus(CatalogMixin, Base):
    __tablename__ = "estado_liquidacion_nomina"


class PayrollSettlement(TimestampMixin, Base):
    __tablename__ = "liquidacion_nomina"
    __table_args__ = (UniqueConstraint("employee_id", "payroll_period_id", name="uq_settlement_employee_period"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("empleado.id"), index=True)
    payroll_period_id: Mapped[int] = mapped_column(ForeignKey("periodo_nomina.id"), index=True)
    status_id: Mapped[int] = mapped_column(ForeignKey("estado_liquidacion_nomina.id"), index=True)
    base_salary: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    earnings_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    deductions_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    net_pay: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    approved_by_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approval_comment: Mapped[str | None] = mapped_column(Text)

    employee: Mapped["Employee"] = relationship()
    period: Mapped[PayrollPeriod] = relationship()
    status: Mapped[PayrollSettlementStatus] = relationship()


class PaySlip(TimestampMixin, Base):
    __tablename__ = "desprendible"
    __table_args__ = (UniqueConstraint("payroll_settlement_id", name="uq_pay_slip_settlement"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    payroll_settlement_id: Mapped[int] = mapped_column(ForeignKey("liquidacion_nomina.id"), index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documento.id"), index=True)


class ContributionsStatus(CatalogMixin, Base):
    __tablename__ = "estado_planilla_aportes"


class ContributionsForm(TimestampMixin, Base):
    __tablename__ = "planilla_aportes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    payroll_period_id: Mapped[int] = mapped_column(ForeignKey("periodo_nomina.id"), index=True)
    status_id: Mapped[int] = mapped_column(ForeignKey("estado_planilla_aportes.id"), index=True)
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documento.id"), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    external_notes: Mapped[str | None] = mapped_column(Text)


class ContributionsDetail(TimestampMixin, Base):
    __tablename__ = "detalle_planilla_aportes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contributions_form_id: Mapped[int] = mapped_column(ForeignKey("planilla_aportes.id"), index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("empleado.id"), index=True)
    contribution_base: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    eps_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    pension_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    arl_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    compensation_fund_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)

