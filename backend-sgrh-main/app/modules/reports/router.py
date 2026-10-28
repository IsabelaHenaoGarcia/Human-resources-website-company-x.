from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.rbac import require_permission
from app.modules.affiliations.models import Affiliation
from app.modules.auth.models import User
from app.modules.certificates.models import EmploymentCertificate
from app.modules.employees.models import Employee
from app.modules.evaluations.models import PerformanceEvaluation
from app.modules.offboarding.models import Offboarding
from app.modules.payroll.models import PayrollSettlement
from app.modules.recruitment.models import Candidate
from app.modules.training.models import TrainingActivity

router = APIRouter(prefix="/reports", tags=["reports"])


def _count(db: Session, model: type) -> int:
    return db.scalar(select(func.count()).select_from(model)) or 0


@router.get("/employees")
def employees_report(db: Session = Depends(get_db), _: User = Depends(require_permission("reports:read"))) -> dict:
    return {"total": _count(db, Employee)}


@router.get("/employees/{employee_id}/history")
def employee_history(employee_id: int, db: Session = Depends(get_db), _: User = Depends(require_permission("reports:read"))) -> dict:
    return {
        "employee_id": employee_id,
        "affiliations": db.scalar(select(func.count()).select_from(Affiliation).where(Affiliation.employee_id == employee_id)) or 0,
        "payroll_settlements": db.scalar(select(func.count()).select_from(PayrollSettlement).where(PayrollSettlement.employee_id == employee_id)) or 0,
        "evaluations": db.scalar(select(func.count()).select_from(PerformanceEvaluation).where(PerformanceEvaluation.employee_id == employee_id)) or 0,
    }


@router.get("/recruitment")
def recruitment_report(db: Session = Depends(get_db), _: User = Depends(require_permission("reports:read"))) -> dict:
    return {"candidates_total": _count(db, Candidate)}


@router.get("/affiliations")
def affiliations_report(db: Session = Depends(get_db), _: User = Depends(require_permission("reports:read"))) -> dict:
    return {"affiliations_total": _count(db, Affiliation)}


@router.get("/payroll")
def payroll_report(db: Session = Depends(get_db), _: User = Depends(require_permission("reports:read"))) -> dict:
    return {"settlements_total": _count(db, PayrollSettlement)}


@router.get("/offboarding")
def offboarding_report(db: Session = Depends(get_db), _: User = Depends(require_permission("reports:read"))) -> dict:
    return {"offboarding_total": _count(db, Offboarding)}


@router.get("/training")
def training_report(db: Session = Depends(get_db), _: User = Depends(require_permission("reports:read"))) -> dict:
    return {"activities_total": _count(db, TrainingActivity)}


@router.get("/evaluations")
def evaluations_report(db: Session = Depends(get_db), _: User = Depends(require_permission("reports:read"))) -> dict:
    return {"evaluations_total": _count(db, PerformanceEvaluation)}


@router.get("/certificates")
def certificates_report(db: Session = Depends(get_db), _: User = Depends(require_permission("reports:read"))) -> dict:
    return {"certificates_total": _count(db, EmploymentCertificate)}
