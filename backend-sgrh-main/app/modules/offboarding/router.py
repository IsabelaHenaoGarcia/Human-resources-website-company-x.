from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.rbac import require_any_permission, require_permission
from app.modules.auth.models import User
from app.modules.documents.models import ContractSettlementDocument, SupportDocumentType
from app.modules.employees.models import Employee
from app.modules.offboarding.models import (
    ContractSettlement,
    ContractSettlementStatus,
    Offboarding,
    OffboardingStatus,
)
from app.modules.recruitment.models import Contract
from app.modules.offboarding.schemas import (
    ContractSettlementCreate,
    ContractSettlementRead,
    ExitChecklistCreate,
    OffboardingCreate,
    OffboardingRead,
)
from app.modules.payroll.schemas import ApprovalRequest
from app.services import audit, create_generated_document, money

router = APIRouter(prefix="/offboarding", tags=["offboarding"])


def _status_id(db: Session, model: type, code: str) -> int:
    row = db.scalar(select(model).where(model.code == code))
    if row is None:
        raise HTTPException(status_code=500, detail=f"Catalog {model.__tablename__}:{code} is missing.")
    return row.id


@router.get("", response_model=list[OffboardingRead])
def list_offboarding(
    db: Session = Depends(get_db),
    _: User = Depends(require_any_permission("offboarding:read", "reports:read")),
) -> list[Offboarding]:
    return list(db.scalars(select(Offboarding).order_by(Offboarding.created_at.desc())).all())


@router.post("", response_model=OffboardingRead, status_code=201)
def create_offboarding(
    payload: OffboardingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("offboarding:write")),
) -> Offboarding:
    if db.get(Employee, payload.empleado_id) is None:
        raise HTTPException(status_code=404, detail="Employee not found.")
    if db.get(Contract, payload.contrato_id) is None:
        raise HTTPException(status_code=404, detail="Contract not found.")
    offboarding = Offboarding(
        employee_id=payload.empleado_id,
        contract_id=payload.contrato_id,
        withdrawal_date=payload.fecha_retiro,
        reason_id=payload.motivo_retiro_id,
        observations=payload.observaciones,
        status_id=payload.estado_retiro_id,
    )
    db.add(offboarding)
    db.flush()
    audit(db, current_user, "create", "retiro_personal", offboarding.id)
    db.commit()
    db.refresh(offboarding)
    return offboarding


@router.post("/{offboarding_id}/exit-checklist", response_model=OffboardingRead)
def register_exit_checklist(
    offboarding_id: int,
    payload: ExitChecklistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("offboarding:write")),
) -> Offboarding:
    offboarding = db.get(Offboarding, offboarding_id)
    if offboarding is None:
        raise HTTPException(status_code=404, detail="Offboarding record not found.")
    offboarding.exit_exam_completed = payload.examen_retiro_realizado
    offboarding.equipment_returned = payload.implementos_entregados
    offboarding.uniforms_returned = payload.dotacion_entregada
    offboarding.checklist_observations = payload.observaciones
    offboarding.status_id = _status_id(db, OffboardingStatus, "in_process")
    audit(db, current_user, "complete_exit_checklist", "retiro_personal", offboarding.id)
    db.commit()
    db.refresh(offboarding)
    return offboarding


@router.post("/{offboarding_id}/contract-settlement", response_model=ContractSettlementRead, status_code=201)
def create_contract_settlement(
    offboarding_id: int,
    payload: ContractSettlementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("offboarding:write")),
) -> ContractSettlement:
    offboarding = db.get(Offboarding, offboarding_id)
    if offboarding is None:
        raise HTTPException(status_code=404, detail="Offboarding record not found.")
    total = money(payload.vacaciones + payload.prima + payload.cesantias + payload.intereses_cesantias - payload.deducciones)
    settlement = ContractSettlement(
        offboarding_id=offboarding_id,
        status_id=payload.estado_liquidacion_id,
        vacation=payload.vacaciones,
        bonus=payload.prima,
        severance=payload.cesantias,
        severance_interest=payload.intereses_cesantias,
        deductions=payload.deducciones,
        total=total,
        observations=payload.observaciones,
    )
    db.add(settlement)
    db.flush()
    content = (
        f"%PDF-1.4\nSGRH CONTRACT SETTLEMENT STUB\nOffboarding: {offboarding_id}\n"
        f"Vacation: {payload.vacaciones}\nBonus: {payload.prima}\nSeverance: {payload.cesantias}\n"
        f"Interest: {payload.intereses_cesantias}\nDeductions: {payload.deducciones}\nTotal: {total}\n%%EOF\n"
    ).encode("utf-8")
    document = create_generated_document(
        db,
        original_filename=f"contract-settlement-{settlement.id}.pdf",
        content=content,
        extension="pdf",
        mime_type="application/pdf",
        user=current_user,
    )
    support = db.scalar(select(SupportDocumentType).where(SupportDocumentType.code == "contract_settlement"))
    if support:
        db.add(
            ContractSettlementDocument(
                contract_settlement_id=settlement.id,
                document_id=document.id,
                support_document_type_id=support.id,
                observation="Generated MVP settlement document.",
            )
        )
    audit(db, current_user, "create", "liquidacion_contrato", settlement.id)
    audit(db, current_user, "generate_contract_settlement_document", "liquidacion_contrato", settlement.id)
    db.commit()
    db.refresh(settlement)
    return settlement


@router.post("/{offboarding_id}/contract-settlement/approve", response_model=ContractSettlementRead)
def approve_contract_settlement(
    offboarding_id: int,
    payload: ApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("contract_settlements:approve")),
) -> ContractSettlement:
    settlement = db.scalar(select(ContractSettlement).where(ContractSettlement.offboarding_id == offboarding_id))
    if settlement is None:
        raise HTTPException(status_code=404, detail="Contract settlement not found.")
    settlement.status_id = _status_id(db, ContractSettlementStatus, "approved")
    settlement.approved_by_id = payload.aprobado_por or current_user.id
    settlement.approved_at = datetime.now(UTC)
    settlement.approval_comment = payload.observacion
    audit(db, current_user, "approve_contract_settlement", "liquidacion_contrato", settlement.id, payload.observacion)
    db.commit()
    db.refresh(settlement)
    return settlement
