from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.core.models import CatalogMixin, TimestampMixin


class AffiliationType(CatalogMixin, Base):
    __tablename__ = "tipo_afiliacion"


class AffiliationStatus(CatalogMixin, Base):
    __tablename__ = "estado_afiliacion"


class Affiliation(TimestampMixin, Base):
    __tablename__ = "afiliacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("empleado.id"), index=True)
    affiliation_type_id: Mapped[int] = mapped_column(ForeignKey("tipo_afiliacion.id"), index=True)
    affiliation_status_id: Mapped[int] = mapped_column(ForeignKey("estado_afiliacion.id"), index=True)
    entity: Mapped[str] = mapped_column(String(160))
    registration_date: Mapped[date] = mapped_column(Date)
    observations: Mapped[str | None] = mapped_column(Text)

    employee: Mapped["Employee"] = relationship()
    affiliation_type: Mapped[AffiliationType] = relationship()
    status: Mapped[AffiliationStatus] = relationship()

