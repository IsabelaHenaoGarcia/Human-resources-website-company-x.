from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.rbac import require_any_permission, require_permission
from app.modules.auth.models import User
from app.modules.employees.models import Employee
from app.modules.recruitment.models import (
    Candidate,
    CandidateStatus,
    CandidateTest,
    Contract,
    Interview,
)
from app.modules.recruitment.schemas import (
    CandidateCreate,
    CandidateRead,
    CandidateTestCreate,
    CandidateUpdate,
    ContractCreate,
    ContractRead,
    InterviewCreate,
    InterviewRead,
    OccupationalExamCreate,
    VerificationCreate,
)
from app.services import audit, ensure_unique_identity
from app.shared.repository import paginate
from app.shared.schemas import PaginatedResponse
from app.shared.status import transition_allowed

router = APIRouter(prefix="/recruitment", tags=["recruitment"])


@router.get("/candidates", response_model=PaginatedResponse[CandidateRead])
def list_candidates(
    q: str | None = None,
    estado_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_any_permission("recruitment:read", "reports:read")),
) -> dict:
    query = select(Candidate).order_by(Candidate.created_at.desc())
    if q:
        like = f"%{q}%"
        query = query.where(or_(Candidate.full_name.ilike(like), Candidate.document_number.ilike(like)))
    if estado_id:
        query = query.where(Candidate.candidate_status_id == estado_id)
    items, total = paginate(db, query, page, page_size)
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.post("/candidates", response_model=CandidateRead, status_code=201)
def create_candidate(
    payload: CandidateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("recruitment:write")),
) -> Candidate:
    ensure_unique_identity(db, payload.document_type_id, payload.document_number)
    candidate = Candidate(**payload.model_dump())
    db.add(candidate)
    db.flush()
    audit(db, current_user, "create", "candidato", candidate.id)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.get("/candidates/{candidate_id}", response_model=CandidateRead)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_any_permission("recruitment:read", "reports:read")),
) -> Candidate:
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return candidate


@router.put("/candidates/{candidate_id}", response_model=CandidateRead)
def update_candidate(
    candidate_id: int,
    payload: CandidateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("recruitment:write")),
) -> Candidate:
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    data = payload.model_dump(exclude_unset=True)
    if "document_type_id" in data or "document_number" in data:
        ensure_unique_identity(
            db,
            data.get("document_type_id", candidate.document_type_id),
            data.get("document_number", candidate.document_number),
            candidate_id=candidate.id,
        )
    if "candidate_status_id" in data:
        target = db.get(CandidateStatus, data["candidate_status_id"])
        if target and not transition_allowed("candidate", candidate.status.code, target.code):
            raise HTTPException(status_code=400, detail="Invalid candidate status transition.")
    for key, value in data.items():
        setattr(candidate, key, value)
    audit(db, current_user, "update", "candidato", candidate.id)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.post("/candidates/{candidate_id}/verifications", response_model=CandidateRead)
def register_verifications(
    candidate_id: int,
    payload: VerificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("recruitment:write")),
) -> Candidate:
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    candidate.references_verified = payload.referencias_verificadas
    candidate.background_verified = payload.antecedentes_verificados
    audit(db, current_user, "register_verification", "candidato", candidate.id, payload.observaciones)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.post("/candidates/{candidate_id}/tests", status_code=201)
def register_test(
    candidate_id: int,
    payload: CandidateTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("recruitment:write")),
) -> dict:
    if db.get(Candidate, candidate_id) is None:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    test = CandidateTest(
        candidate_id=candidate_id,
        test_type=payload.tipo_prueba,
        result=payload.resultado,
        observations=payload.observaciones,
    )
    db.add(test)
    db.flush()
    audit(db, current_user, "register_test", "prueba_candidato", test.id)
    db.commit()
    return {"id": test.id}


@router.post("/candidates/{candidate_id}/occupational-exam", response_model=CandidateRead)
def register_occupational_exam(
    candidate_id: int,
    payload: OccupationalExamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("recruitment:write")),
) -> Candidate:
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    candidate.occupational_exam_date = payload.fecha
    candidate.occupational_exam_result = payload.resultado
    candidate.occupational_exam_observations = payload.observaciones
    audit(db, current_user, "register_occupational_exam", "candidato", candidate.id)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.post("/interviews", response_model=InterviewRead, status_code=201)
def create_interview(
    payload: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("recruitment:write")),
) -> Interview:
    if db.get(Candidate, payload.candidato_id) is None:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    interview = Interview(
        candidate_id=payload.candidato_id,
        scheduled_at=payload.fecha_hora,
        interviewer=payload.entrevistador,
        result=payload.resultado,
        observations=payload.observaciones,
        status_id=payload.estado_entrevista_id,
    )
    db.add(interview)
    db.flush()
    audit(db, current_user, "create", "entrevista", interview.id)
    db.commit()
    db.refresh(interview)
    return interview


@router.post("/contracts", response_model=ContractRead, status_code=201)
def create_contract(
    payload: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("recruitment:write")),
) -> Contract:
    if db.get(Employee, payload.empleado_id) is None:
        raise HTTPException(status_code=404, detail="Employee not found.")
    contract = Contract(
        employee_id=payload.empleado_id,
        contract_type_id=payload.tipo_contrato_id,
        contract_status_id=payload.estado_contrato_id,
        position=payload.cargo,
        base_salary=payload.salario_base,
        start_date=payload.fecha_inicio,
        end_date=payload.fecha_fin,
    )
    db.add(contract)
    db.flush()
    audit(db, current_user, "create", "contrato", contract.id)
    db.commit()
    db.refresh(contract)
    return contract


@router.get("/contracts", response_model=list[ContractRead])
def list_contracts(
    db: Session = Depends(get_db),
    _: User = Depends(require_any_permission("recruitment:read", "payroll:read")),
) -> list[Contract]:
    return list(db.scalars(select(Contract).order_by(Contract.start_date.desc())).all())
