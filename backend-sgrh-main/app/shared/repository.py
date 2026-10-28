from typing import Any, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


def get_or_404(db: Session, model: type[ModelT], object_id: int) -> ModelT | None:
    return db.get(model, object_id)


def paginate(db: Session, query: Select[Any], page: int, page_size: int) -> tuple[list[Any], int]:
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = db.scalars(query.offset((page - 1) * page_size).limit(page_size)).all()
    return list(items), total

