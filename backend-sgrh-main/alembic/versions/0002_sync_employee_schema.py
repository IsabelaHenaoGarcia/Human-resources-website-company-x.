"""sync employee schema

Revision ID: 0002_sync_employee_schema
Revises: 0001_initial_schema_and_seed
Create Date: 2026-05-30
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_sync_employee_schema"
down_revision = "0001_initial_schema_and_seed"
branch_labels = None
depends_on = None


def _columns(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns(table_name)}


def _add_column_if_missing(existing_columns: set[str], column: sa.Column) -> None:
    if column.name not in existing_columns:
        op.add_column("empleado", column)


def upgrade() -> None:
    existing_columns = _columns("empleado")
    _add_column_if_missing(existing_columns, sa.Column("user_id", sa.Integer(), nullable=True))
    _add_column_if_missing(existing_columns, sa.Column("birth_date", sa.Date(), nullable=True))
    _add_column_if_missing(existing_columns, sa.Column("address", sa.String(length=255), nullable=True))
    _add_column_if_missing(existing_columns, sa.Column("eps_entity", sa.String(length=160), nullable=True))
    _add_column_if_missing(existing_columns, sa.Column("pension_entity", sa.String(length=160), nullable=True))
    _add_column_if_missing(existing_columns, sa.Column("has_beneficiaries", sa.Boolean(), nullable=True))
    _add_column_if_missing(existing_columns, sa.Column("beneficiary_notes", sa.Text(), nullable=True))
    _add_column_if_missing(existing_columns, sa.Column("induction_completed", sa.Boolean(), nullable=True))


def downgrade() -> None:
    existing_columns = _columns("empleado")
    for column_name in (
        "induction_completed",
        "beneficiary_notes",
        "has_beneficiaries",
        "pension_entity",
        "eps_entity",
        "address",
        "birth_date",
        "user_id",
    ):
        if column_name in existing_columns:
            op.drop_column("empleado", column_name)
