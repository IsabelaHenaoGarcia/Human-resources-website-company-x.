from datetime import UTC, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.rbac import require_any_permission, require_permission
from app.modules.auth.models import User
from app.modules.documents.models import Document
from app.modules.employees.models import Employee
from app.modules.payroll.models import (
    ContributionsDetail,
    ContributionsForm,
    ContributionsStatus,
    PaySlip,
    PayrollNovelty,
    PayrollNoveltyType,
    PayrollPeriod,
    PayrollPeriodStatus,
    PayrollSettlement,
    PayrollSettlementStatus,
)
from app.modules.documents.schemas import DocumentRead
from app.modules.payroll.schemas import (
    ApprovalRequest,
    PayrollNoveltyCreate,
    PayrollNoveltyRead,
    PayrollPeriodCreate,
    PayrollPeriodRead,
    PayrollSettlementRead,
)
from app.services import audit, create_generated_document, money

router = APIRouter(prefix="/payroll", tags=["payroll"])


def _catalog_id(db: Session, model: type, code: str) -> int:
    row = db.scalar(select(model).where(model.code == code))
    if row is None:
        raise HTTPException(status_code=500, detail=f"Catalog {model.__tablename__}:{code} is missing.")
    return row.id


@router.get("/periods", response_model=list[PayrollPeriodRead])
def list_periods(
    db: Session = Depends(get_db),
    _: User = Depends(require_any_permission("payroll:read", "reports:read")),
) -> list[PayrollPeriod]:
    return list(db.scalars(select(PayrollPeriod).order_by(PayrollPeriod.start_date.desc())).all())


@router.post("/periods", response_model=PayrollPeriodRead, status_code=201)
def create_period(
    payload: PayrollPeriodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("payroll:write")),
) -> PayrollPeriod:
    if payload.start_date > payload.end_date:
        raise HTTPException(status_code=400, detail="Payroll period start_date must be before end_date.")
    period = PayrollPeriod(**payload.model_dump())
    db.add(period)
    db.flush()
    audit(db, current_user, "create", "periodo_nomina", period.id)
    db.commit()
    db.refresh(period)
    return period


@router.post("/periods/{period_id}/novelties", response_model=PayrollNoveltyRead, status_code=201)
def create_novelty(
    period_id: int,
    payload: PayrollNoveltyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("payroll:write")),
) -> PayrollNovelty:
    if db.get(PayrollPeriod, period_id) is None:
        raise HTTPException(status_code=404, detail="Payroll period not found.")
    if db.get(Employee, payload.empleado_id) is None:
        raise HTTPException(status_code=404, detail="Employee not found.")
    novelty_type = db.scalar(select(PayrollNoveltyType).where(PayrollNoveltyType.code == payload.tipo_novedad_codigo))
    if novelty_type is None:
        raise HTTPException(status_code=400, detail="Invalid payroll novelty type.")
    novelty = PayrollNovelty(
        employee_id=payload.empleado_id,
        payroll_period_id=period_id,
        novelty_type_id=novelty_type.id,
        document_id=payload.documento_id,
        application_date=payload.fecha_aplicacion,
        amount=payload.valor,
        hours=payload.cantidad_horas,
        observations=payload.observaciones,
    )
    db.add(novelty)
    db.flush()
    audit(db, current_user, "create", "novedad_nomina", novelty.id)
    db.commit()
    db.refresh(novelty)
    return novelty


@router.post("/periods/{period_id}/settle", response_model=list[PayrollSettlementRead])
def settle_period(
    period_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("payroll:write")),
) -> list[PayrollSettlement]:
    period = db.get(PayrollPeriod, period_id)
    if period is None:
        raise HTTPException(status_code=404, detail="Payroll period not found.")
    if period.status.code == "closed":
        raise HTTPException(status_code=400, detail="Cannot settle a closed payroll period.")
    status_id = _catalog_id(db, PayrollSettlementStatus, "generated")
    employees = db.scalars(select(Employee)).all()
    results: list[PayrollSettlement] = []
    for employee in employees:
        existing = db.scalar(
            select(PayrollSettlement).where(
                PayrollSettlement.employee_id == employee.id,
                PayrollSettlement.payroll_period_id == period_id,
            )
        )
        if existing:
            results.append(existing)
            continue
        novelties = db.scalars(
            select(PayrollNovelty).join(PayrollNoveltyType).where(
                PayrollNovelty.employee_id == employee.id,
                PayrollNovelty.payroll_period_id == period_id,
            )
        ).all()
        earnings = Decimal("0")
        deductions = Decimal("0")
        for novelty in novelties:
            if novelty.novelty_type.calculation_effect == "earning":
                earnings += money(novelty.amount)
            elif novelty.novelty_type.calculation_effect == "deduction":
                deductions += money(novelty.amount)
        base_salary = money(employee.base_salary)
        settlement = PayrollSettlement(
            employee_id=employee.id,
            payroll_period_id=period_id,
            status_id=status_id,
            base_salary=base_salary,
            earnings_total=earnings,
            deductions_total=deductions,
            net_pay=base_salary + earnings - deductions,
        )
        db.add(settlement)
        results.append(settlement)
    period.status_id = _catalog_id(db, PayrollPeriodStatus, "in_review")
    db.flush()
    audit(db, current_user, "settle", "periodo_nomina", period.id)
    db.commit()
    return results


@router.post("/periods/{period_id}/review", response_model=PayrollPeriodRead)
def review_period(
    period_id: int,
    payload: ApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("payroll:approve")),
) -> PayrollPeriod:
    period = db.get(PayrollPeriod, period_id)
    if period is None:
        raise HTTPException(status_code=404, detail="Payroll period not found.")
    if payload.aprobado_por_gerencia:
        period.status_id = _catalog_id(db, PayrollPeriodStatus, "approved")
        period.approved_by_id = current_user.id
        period.approved_at = datetime.now(UTC)
        period.approval_comment = payload.observacion
        settlement_status = _catalog_id(db, PayrollSettlementStatus, "approved")
        for settlement in db.scalars(select(PayrollSettlement).where(PayrollSettlement.payroll_period_id == period_id)):
            settlement.status_id = settlement_status
            settlement.approved_by_id = current_user.id
            settlement.approved_at = period.approved_at
            settlement.approval_comment = payload.observacion
    audit(db, current_user, "approve_payroll", "periodo_nomina", period.id, payload.observacion)
    db.commit()
    db.refresh(period)
    return period


@router.get("/settlements", response_model=list[PayrollSettlementRead])
def list_settlements(
    db: Session = Depends(get_db),
    _: User = Depends(require_any_permission("payroll:read", "reports:read")),
) -> list[PayrollSettlement]:
    return list(db.scalars(select(PayrollSettlement).order_by(PayrollSettlement.created_at.desc())).all())


@router.get("/settlements/{settlement_id}", response_model=PayrollSettlementRead)
def get_settlement(
    settlement_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_any_permission("payroll:read", "reports:read")),
) -> PayrollSettlement:
    settlement = db.get(PayrollSettlement, settlement_id)
    if settlement is None:
        raise HTTPException(status_code=404, detail="Payroll settlement not found.")
    return settlement


@router.get("/periods/{period_id}/general-report", response_model=DocumentRead)
def general_report(
    period_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_permission("payroll:read", "reports:read")),
):
    period = db.get(PayrollPeriod, period_id)
    if period is None:
        raise HTTPException(status_code=404, detail="Payroll period not found.")
    lines = ["employee_id,base_salary,earnings_total,deductions_total,net_pay"]
    for s in db.scalars(select(PayrollSettlement).where(PayrollSettlement.payroll_period_id == period_id)):
        lines.append(f"{s.employee_id},{s.base_salary},{s.earnings_total},{s.deductions_total},{s.net_pay}")
    document = create_generated_document(
        db,
        original_filename=f"payroll-general-report-{period_id}.csv",
        content="\n".join(lines).encode("utf-8"),
        extension="csv",
        mime_type="text/csv",
        user=current_user,
    )
    audit(db, current_user, "generate_payroll_report", "periodo_nomina", period_id)
    db.commit()
    db.refresh(document)
    return document


@router.post("/settlements/{settlement_id}/pay-slip", response_model=DocumentRead, status_code=201)
def generate_pay_slip(
    settlement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("payroll:write")),
):
    settlement = db.get(PayrollSettlement, settlement_id)
    if settlement is None:
        raise HTTPException(status_code=404, detail="Payroll settlement not found.")
    existing = db.scalar(select(PaySlip).where(PaySlip.payroll_settlement_id == settlement_id))
    if existing:
        return db.get(Document, existing.document_id)
    employee = settlement.employee
    period = settlement.period
    content = (
        f"%PDF-1.4\nSGRH PAY SLIP STUB\nCompany: {settings.company_name}\n"
        f"Period: {period.start_date} - {period.end_date}\nEmployee: {employee.full_name}\n"
        f"Document: {employee.document_number}\nPosition: {employee.position}\nBase salary: {settlement.base_salary}\n"
        f"Earnings: {settlement.earnings_total}\nDeductions: {settlement.deductions_total}\n"
        f"Net pay: {settlement.net_pay}\nGenerated: {datetime.now(UTC).isoformat()}\nReference: {settlement.id}\n%%EOF\n"
    ).encode("utf-8")
    document = create_generated_document(
        db,
        original_filename=f"pay-slip-{settlement.id}.pdf",
        content=content,
        extension="pdf",
        mime_type="application/pdf",
        user=current_user,
    )
    db.add(PaySlip(payroll_settlement_id=settlement.id, document_id=document.id))
    audit(db, current_user, "generate_pay_slip", "liquidacion_nomina", settlement.id)
    db.commit()
    db.refresh(document)
    return document


@router.post("/periods/{period_id}/contributions", status_code=201)
def create_contributions(
    period_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("payroll:write")),
) -> dict:
    if db.get(PayrollPeriod, period_id) is None:
        raise HTTPException(status_code=404, detail="Payroll period not found.")
    form = ContributionsForm(payroll_period_id=period_id, status_id=_catalog_id(db, ContributionsStatus, "generated"))
    db.add(form)
    db.flush()
    for settlement in db.scalars(select(PayrollSettlement).where(PayrollSettlement.payroll_period_id == period_id)):
        base = money(settlement.base_salary + settlement.earnings_total)
        eps = money(base * Decimal("0.04"))
        pension = money(base * Decimal("0.04"))
        arl = money(base * Decimal("0.005"))
        fund = money(base * Decimal("0.04"))
        db.add(
            ContributionsDetail(
                contributions_form_id=form.id,
                employee_id=settlement.employee_id,
                contribution_base=base,
                eps_amount=eps,
                pension_amount=pension,
                arl_amount=arl,
                compensation_fund_amount=fund,
                total_amount=eps + pension + arl + fund,
            )
        )
    audit(db, current_user, "generate_contributions", "planilla_aportes", form.id)
    db.commit()
    return {"id": form.id, "status": "generated"}


@router.post("/periods/{period_id}/contributions/export", response_model=DocumentRead, status_code=201)
def export_contributions(
    period_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("payroll:write")),
):
    form = db.scalar(select(ContributionsForm).where(ContributionsForm.payroll_period_id == period_id))
    if form is None:
        raise HTTPException(status_code=404, detail="Contributions form not found.")
    lines = ["employee_id,contribution_base,eps,pension,arl,compensation_fund,total"]
    for detail in db.scalars(select(ContributionsDetail).where(ContributionsDetail.contributions_form_id == form.id)):
        lines.append(
            f"{detail.employee_id},{detail.contribution_base},{detail.eps_amount},{detail.pension_amount},"
            f"{detail.arl_amount},{detail.compensation_fund_amount},{detail.total_amount}"
        )
    document = create_generated_document(
        db,
        original_filename=f"contributions-{period_id}.csv",
        content="\n".join(lines).encode("utf-8"),
        extension="csv",
        mime_type="text/csv",
        user=current_user,
    )
    form.document_id = document.id
    form.status_id = _catalog_id(db, ContributionsStatus, "exported")
    audit(db, current_user, "export_contributions", "planilla_aportes", form.id)
    db.commit()
    db.refresh(document)
    return document
