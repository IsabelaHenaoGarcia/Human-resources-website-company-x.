from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.config import settings
from app.core.db import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.modules.auth.models import Role, User, UserStatus
from app.seed import seed_all


@pytest.fixture()
def db_session(tmp_path) -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    previous_storage_path = settings.storage_path
    previous_initial_admin_password = settings.initial_admin_password
    settings.storage_path = str(tmp_path / "storage")
    settings.initial_admin_password = None
    try:
        seed_all(session)
        active_status = session.scalar(select(UserStatus).where(UserStatus.code == "active"))
        admin_role = session.scalar(select(Role).where(Role.code == "ADMIN"))
        session.add(
            User(
                username="admin",
                password_hash=hash_password("Admin123!"),
                full_name="Test Admin",
                status_id=active_status.id,
                roles=[admin_role],
            )
        )
        session.commit()
        yield session
    finally:
        session.close()
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        settings.storage_path = previous_storage_path
        settings.initial_admin_password = previous_initial_admin_password
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post("/auth/login", json={"username": "admin", "password": "Admin123!"})
    assert response.status_code == 200, response.text
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}
