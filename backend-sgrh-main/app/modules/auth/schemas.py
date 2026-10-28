from pydantic import BaseModel, Field

from app.shared.schemas import ORMModel


class UserRead(ORMModel):
    id: int
    username: str
    full_name: str | None = None
    roles: list[str] = []
    permissions: list[str] = []


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    user: UserRead
    token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str
    password: str = Field(min_length=8)
    full_name: str | None = None
    role_codes: list[str] = Field(default_factory=list)
    active: bool = True


class UserUpdate(BaseModel):
    password: str | None = Field(default=None, min_length=8)
    full_name: str | None = None
    role_codes: list[str] | None = None
    active: bool | None = None

