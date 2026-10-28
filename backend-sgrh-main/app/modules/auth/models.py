from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.core.models import CatalogMixin, TimestampMixin


class UserStatus(CatalogMixin, Base):
    __tablename__ = "estado_usuario"


class Role(CatalogMixin, Base):
    __tablename__ = "rol"

    users: Mapped[list["User"]] = relationship(secondary="usuario_rol", back_populates="roles")
    permissions: Mapped[list["Permission"]] = relationship(secondary="rol_permiso", back_populates="roles")


class Permission(CatalogMixin, Base):
    __tablename__ = "permiso"

    roles: Mapped[list[Role]] = relationship(secondary="rol_permiso", back_populates="permissions")


class User(TimestampMixin, Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    status_id: Mapped[int] = mapped_column(ForeignKey("estado_usuario.id"), index=True)
    full_name: Mapped[str | None] = mapped_column(String(160))

    status: Mapped[UserStatus] = relationship()
    roles: Mapped[list[Role]] = relationship(secondary="usuario_rol", back_populates="users")


class UserRole(Base):
    __tablename__ = "usuario_rol"

    user_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("rol.id"), primary_key=True)


class RolePermission(Base):
    __tablename__ = "rol_permiso"

    role_id: Mapped[int] = mapped_column(ForeignKey("rol.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permiso.id"), primary_key=True)

