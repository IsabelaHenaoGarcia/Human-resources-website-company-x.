from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.core.models import CatalogMixin, TimestampMixin


class CandidateStatus(CatalogMixin, Base):
    __tablename__ = "estado_candidato"


class Candidate(TimestampMixin, Base):
    __tablename__ = "candidato"
    __table_args__ = (UniqueConstraint("document_type_id", "document_number", name="uq_candidate_identity"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_type_id: Mapped[int] = mapped_column(ForeignKey("tipo_documento.id"), index=True)
    candidate_status_id: Mapped[int] = mapped_column(ForeignKey("estado_candidato.id"), index=True)
    full_name: Mapped[str] = mapped_column(String(160), index=True)
    document_number: Mapped[str] = mapped_column(String(50), index=True)
    email: Mapped[str | None] = mapped_column(String(160))
    phone: Mapped[str | None] = mapped_column(String(50))
    position_applied: Mapped[str | None] = mapped_column(String(120))
    interview_result_summary: Mapped[str | None] = mapped_column(Text)
    references_verified: Mapped[bool] = mapped_column(default=False)
    background_verified: Mapped[bool] = mapped_column(default=False)
    occupational_exam_date: Mapped[date | None] = mapped_column(Date)
    occupational_exam_result: Mapped[str | None] = mapped_column(String(80))
    occupational_exam_observations: Mapped[str | None] = mapped_column(Text)

    document_type: Mapped["DocumentType"] = relationship()
    status: Mapped[CandidateStatus] = relationship()


class InterviewStatus(CatalogMixin, Base):
    __tablename__ = "estado_entrevista"


class Interview(TimestampMixin, Base):
    __tablename__ = "entrevista"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidato.id"), index=True)
    status_id: Mapped[int] = mapped_column(ForeignKey("estado_entrevista.id"), index=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    interviewer: Mapped[str] = mapped_column(String(160))
    result: Mapped[str | None] = mapped_column(String(120))
    observations: Mapped[str | None] = mapped_column(Text)

    candidate: Mapped[Candidate] = relationship()
    status: Mapped[InterviewStatus] = relationship()


class CandidateTest(TimestampMixin, Base):
    __tablename__ = "prueba_candidato"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidato.id"), index=True)
    test_type: Mapped[str] = mapped_column(String(120))
    result: Mapped[str] = mapped_column(String(120))
    observations: Mapped[str | None] = mapped_column(Text)


class ContractType(CatalogMixin, Base):
    __tablename__ = "tipo_contrato"


class ContractStatus(CatalogMixin, Base):
    __tablename__ = "estado_contrato"


class Contract(TimestampMixin, Base):
    __tablename__ = "contrato"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("empleado.id"), index=True)
    contract_type_id: Mapped[int] = mapped_column(ForeignKey("tipo_contrato.id"), index=True)
    contract_status_id: Mapped[int] = mapped_column(ForeignKey("estado_contrato.id"), index=True)
    position: Mapped[str] = mapped_column(String(120))
    base_salary: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    start_date: Mapped[date] = mapped_column(Date, index=True)
    end_date: Mapped[date | None] = mapped_column(Date)

    employee: Mapped["Employee"] = relationship()
    contract_type: Mapped[ContractType] = relationship()
    status: Mapped[ContractStatus] = relationship()

