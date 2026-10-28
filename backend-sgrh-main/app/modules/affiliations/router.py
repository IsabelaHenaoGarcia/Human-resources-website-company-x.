from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.rbac import require_any_permission, require_permission
from app.modules.affiliations.models import Affiliation, AffiliationStatus
from app.modules.auth.models import User
from app.modules.employees.models import Employee
from app.modules.affiliations.schemas import AffiliationCreate, AffiliationRead, AffiliationUpdate
from app.services import audit
from app.shared.status import transition_allowed

router = APIRouter(prefix="/affiliations", tags=["affiliations"])


@router.get("", response_model=list[AffiliationRead])
def list_affiliations(
    empleado_id: int | None = None,
    tipo_afiliacion_id: int | None = None,
    estado_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_any_permission("affiliations:read", "reports:read")),
) -> list[Affiliation]:
    query = select(Affiliation).order_by(Affiliation.created_at.desc())
    if empleado_id:
        query = query.where(Affiliation.employee_id == empleado_id)
    if tipo_afiliacion_id:
        query = query.where(Affiliation.affiliation_type_id == tipo_afiliacion_id)
    if estado_id:
        query = query.where(Affiliation.affiliation_status_id == estado_id)
    return list(db.scalars(query).all())


@router.post("", response_model=AffiliationRead, status_code=201)
def create_affiliation(
    payload: AffiliationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("affiliations:write")),
) -> Affiliation:
    if db.get(Employee, payload.empleado_id) is None:
        raise HTTPException(status_code=404, detail="Employee not found.")
    affiliation = Affiliation(
        employee_id=payload.empleado_id,
        affiliation_type_id=payload.tipo_afiliacion_id,
        affiliation_status_id=payload.estado_afiliacion_id,
        entity=payload.entidad,
        registration_date=payload.fecha_registro,
        observations=payload.observaciones,
    )
    db.add(affiliation)
    db.flush()
    audit(db, current_user, "create", "afiliacion", affiliation.id)
    db.commit()
    db.refresh(affiliation)
    return affiliation


@router.put("/{affiliation_id}", response_model=AffiliationRead)
def update_affiliation(
    affiliation_id: int,
    payload: AffiliationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("affiliations:write")),
) -> Affiliation:
    affiliation = db.get(Affiliation, affiliation_id)
    if affiliation is None:
        raise HTTPException(status_code=404, detail="Affiliation not found.")
    data = payload.model_dump(exclude_unset=True)
    if "estado_afiliacion_id" in data:
        target = db.get(AffiliationStatus, data["estado_afiliacion_id"])
        if target and not transition_allowed("affiliation", affiliation.status.code, target.code):
            raise HTTPException(status_code=400, detail="Invalid affiliation status transition.")
    mapping = {
        "tipo_afiliacion_id": "affiliation_type_id",
        "estado_afiliacion_id": "affiliation_status_id",
        "entidad": "entity",
        "fecha_registro": "registration_date",
        "observaciones": "observations",
    }
    for key, value in data.items():
        setattr(affiliation, mapping[key], value)
    audit(db, current_user, "update", "afiliacion", affiliation.id)
    db.commit()
    db.refresh(affiliation)
    return affiliation
