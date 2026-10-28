from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.db import get_db
from app.core.rbac import get_current_user
from app.core.security import create_access_token, verify_password
from app.modules.auth.models import Role, User
from app.modules.auth.schemas import LoginRequest, LoginResponse, UserRead
from app.services import audit, build_user_read

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.scalar(
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions), selectinload(User.status))
        .where(User.username == payload.username)
    )
    if user is None or user.status.code != "active" or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    token = create_access_token(str(user.id))
    audit(db, user, "login", "usuario", user.id)
    db.commit()
    return LoginResponse(user=UserRead(**build_user_read(user)), token=token)


@router.post("/logout", status_code=204)
def logout(response: Response, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    audit(db, current_user, "logout", "usuario", current_user.id)
    db.commit()
    response.delete_cookie("access_token")


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead(**build_user_read(current_user))
