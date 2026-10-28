"""initial schema and seed data

Revision ID: 0001_initial_schema_and_seed
Revises:
Create Date: 2026-05-18
"""

from alembic import op
from sqlalchemy.orm import Session

from app.core.db import Base
from app import models  # noqa: F401
from app.seed import seed_all

revision = "0001_initial_schema_and_seed"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)
    session = Session(bind=bind)
    try:
        seed_all(session)
    finally:
        session.close()


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)

