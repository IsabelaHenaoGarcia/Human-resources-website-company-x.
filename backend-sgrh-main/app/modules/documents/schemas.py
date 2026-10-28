from datetime import datetime

from pydantic import BaseModel

from app.shared.schemas import ORMModel


class DocumentRead(ORMModel):
    id: int
    original_filename: str
    stored_filename: str
    storage_path: str
    mime_type: str | None
    file_size: int
    generated: bool
    file_type_id: int
    created_at: datetime


class DocumentLinkCreate(BaseModel):
    document_id: int
    support_document_type_id: int
    observation: str | None = None

