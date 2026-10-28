from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.db import get_db
from app.core.rbac import require_permission
from app.core.security import hash_password
from app.modules.auth.models import Permission, Role, User, UserStatus
from app.modules.auth.schemas import UserCreate, UserRead, UserUpdate
from app.shared.schemas import CatalogRead
from app.services import audit, build_user_read

router = APIRouter(prefix="/admin", tags=["admin"])


def _role_objects(db: Session, role_codes: list[str]) -> list[Role]:
    roles = db.scalars(select(Role).where(Role.code.in_(role_codes))).all()
    if len(roles) != len(set(role_codes)):
        raise HTTPException(status_code=400, detail="One or more roles do not exist.")
    return list(roles)


@router.get("/users", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("admin:users")),
) -> list[UserRead]:
    users = db.scalars(select(User).options(selectinload(User.roles).selectinload(Role.permissions))).all()
    return [UserRead(**build_user_read(user)) for user in users]


@router.post("/users", response_model=UserRead, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("admin:users")),
) -> UserRead:
    if db.scalar(select(User).where(User.username == payload.username)):
        raise HTTPException(status_code=409, detail="Username already exists.")
    status_code = "active" if payload.active else "inactive"
    status = db.scalar(select(UserStatus).where(UserStatus.code == status_code))
    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        status_id=status.id,
        roles=_role_objects(db, payload.role_codes),
    )
    db.add(user)
    db.flush()
    audit(db, current_user, "create", "usuario", user.id)
    db.commit()
    db.refresh(user)
    return UserRead(**build_user_read(user))


@router.put("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("admin:users")),
) -> UserRead:
    user = db.scalar(select(User).options(selectinload(User.roles).selectinload(Role.permissions)).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    if payload.password is not None:
        user.password_hash = hash_password(payload.password)
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.active is not None:
        user.status_id = db.scalar(select(UserStatus).where(UserStatus.code == ("active" if payload.active else "inactive"))).id
    if payload.role_codes is not None:
        user.roles = _role_objects(db, payload.role_codes)
    audit(db, current_user, "update", "usuario", user.id)
    db.commit()
    db.refresh(user)
    return UserRead(**build_user_read(user))


@router.get("/roles", response_model=list[CatalogRead])
def list_roles(_: User = Depends(require_permission("admin:roles")), db: Session = Depends(get_db)) -> list[Role]:
    return list(db.scalars(select(Role).order_by(Role.code)).all())


@router.get("/permissions", response_model=list[CatalogRead])
def list_permissions(_: User = Depends(require_permission("admin:roles")), db: Session = Depends(get_db)) -> list[Permission]:
    return list(db.scalars(select(Permission).order_by(Permission.code)).all())
