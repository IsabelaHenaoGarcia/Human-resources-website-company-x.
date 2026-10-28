from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.core.models import CatalogMixin, TimestampMixin


class EmployeeStatus(CatalogMixin, Base):
    __tablename__ = "estado_empleado"


class Employee(TimestampMixin, Base):
    __tablename__ = "empleado"
    __table_args__ = (
        UniqueConstraint("document_type_id", "document_number", name="uq_employee_identity"),
        Index("ix_employee_name_document", "full_name", "document_number"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"), unique=True, nullable=True)
    document_type_id: Mapped[int] = mapped_column(ForeignKey("tipo_documento.id"), index=True)
    employee_status_id: Mapped[int] = mapped_column(ForeignKey("estado_empleado.id"), index=True)
    full_name: Mapped[str] = mapped_column(String(160), index=True)
    document_number: Mapped[str] = mapped_column(String(50), index=True)
    birth_date: Mapped[date | None] = mapped_column(Date)
    email: Mapped[str | None] = mapped_column(String(160))
    phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(String(255))
    position: Mapped[str] = mapped_column(String(120))
    hire_date: Mapped[date] = mapped_column(Date)
    base_salary: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    eps_entity: Mapped[str | None] = mapped_column(String(160))
    pension_entity: Mapped[str | None] = mapped_column(String(160))
    has_beneficiaries: Mapped[bool] = mapped_column(Boolean, default=False)
    beneficiary_notes: Mapped[str | None] = mapped_column(Text)
    induction_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    latest_evaluation_status: Mapped[str | None] = mapped_column(String(80))
    latest_evaluation_date: Mapped[date | None] = mapped_column(Date)

    document_type: Mapped["DocumentType"] = relationship()
    status: Mapped[EmployeeStatus] = relationship()

