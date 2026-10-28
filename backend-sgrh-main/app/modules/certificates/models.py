from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.core.models import CatalogMixin, TimestampMixin


class CertificateType(CatalogMixin, Base):
    __tablename__ = "tipo_certificacion_laboral"


class CertificateStatus(CatalogMixin, Base):
    __tablename__ = "estado_certificacion_laboral"


class EmploymentCertificate(TimestampMixin, Base):
    __tablename__ = "certificacion_laboral"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("empleado.id"), index=True)
    certificate_type_id: Mapped[int] = mapped_column(ForeignKey("tipo_certificacion_laboral.id"), index=True)
    status_id: Mapped[int] = mapped_column(ForeignKey("estado_certificacion_laboral.id"), index=True)
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documento.id"), nullable=True)
    observation: Mapped[str | None] = mapped_column(Text)

