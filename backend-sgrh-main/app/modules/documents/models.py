from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.core.models import CatalogMixin, TimestampMixin


class DocumentType(CatalogMixin, Base):
    __tablename__ = "tipo_documento"


class FileType(CatalogMixin, Base):
    __tablename__ = "tipo_archivo"


class SupportDocumentType(CatalogMixin, Base):
    __tablename__ = "tipo_documento_soporte"


class Document(TimestampMixin, Base):
    __tablename__ = "documento"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_type_id: Mapped[int] = mapped_column(ForeignKey("tipo_archivo.id"), index=True)
    uploaded_by_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"), nullable=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    stored_filename: Mapped[str] = mapped_column(String(255))
    storage_path: Mapped[str] = mapped_column(String(500))
    mime_type: Mapped[str | None] = mapped_column(String(120))
    file_size: Mapped[int] = mapped_column(Integer)
    generated: Mapped[bool] = mapped_column(Boolean, default=False)

    file_type: Mapped[FileType] = relationship()


class DocumentLinkMixin(TimestampMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documento.id"), index=True)
    support_document_type_id: Mapped[int] = mapped_column(ForeignKey("tipo_documento_soporte.id"), index=True)
    observation: Mapped[str | None] = mapped_column(Text)


class EmployeeDocument(DocumentLinkMixin, Base):
    __tablename__ = "documento_empleado"

    employee_id: Mapped[int] = mapped_column(ForeignKey("empleado.id"), index=True)


class CandidateDocument(DocumentLinkMixin, Base):
    __tablename__ = "documento_candidato"

    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidato.id"), index=True)


class ContractDocument(DocumentLinkMixin, Base):
    __tablename__ = "documento_contrato"

    contract_id: Mapped[int] = mapped_column(ForeignKey("contrato.id"), index=True)


class AffiliationDocument(DocumentLinkMixin, Base):
    __tablename__ = "documento_afiliacion"

    affiliation_id: Mapped[int] = mapped_column(ForeignKey("afiliacion.id"), index=True)


class OffboardingDocument(DocumentLinkMixin, Base):
    __tablename__ = "documento_retiro_personal"

    offboarding_id: Mapped[int] = mapped_column(ForeignKey("retiro_personal.id"), index=True)


class ContractSettlementDocument(DocumentLinkMixin, Base):
    __tablename__ = "documento_liquidacion_contrato"

    contract_settlement_id: Mapped[int] = mapped_column(ForeignKey("liquidacion_contrato.id"), index=True)


class TrainingActivityDocument(DocumentLinkMixin, Base):
    __tablename__ = "documento_actividad_formativa"

    training_activity_id: Mapped[int] = mapped_column(ForeignKey("actividad_formativa.id"), index=True)

