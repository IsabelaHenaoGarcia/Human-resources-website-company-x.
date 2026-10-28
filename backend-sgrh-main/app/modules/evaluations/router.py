from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.rbac import require_any_permission, require_permission
from app.modules.auth.models import User
from app.modules.employees.models import Employee
from app.modules.evaluations.models import EvaluationStatus, ImprovementPlan, PerformanceEvaluation
from app.modules.evaluations.schemas import EvaluationCreate, EvaluationRead, ImprovementPlanCreate
from app.services import audit

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.get("", response_model=list[EvaluationRead])
def list_evaluations(
    db: Session = Depends(get_db),
    _: User = Depends(require_any_permission("evaluations:read", "reports:read")),
) -> list[PerformanceEvaluation]:
    return list(db.scalars(select(PerformanceEvaluation).order_by(PerformanceEvaluation.evaluation_date.desc())).all())


@router.post("", response_model=EvaluationRead, status_code=201)
def create_evaluation(
    payload: EvaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("evaluations:write")),
) -> PerformanceEvaluation:
    employee = db.get(Employee, payload.empleado_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found.")
    evaluation = PerformanceEvaluation(
        employee_id=payload.empleado_id,
        status_id=payload.estado_evaluacion_id,
        evaluation_type=payload.tipo_evaluacion,
        evaluation_date=payload.fecha_evaluacion,
        score=payload.puntaje,
        observations=payload.observaciones,
    )
    db.add(evaluation)
    employee.latest_evaluation_date = payload.fecha_evaluacion
    status = db.get(EvaluationStatus, payload.estado_evaluacion_id)
    employee.latest_evaluation_status = status.code if status else None
    db.flush()
    audit(db, current_user, "create", "evaluacion_desempeno", evaluation.id)
    db.commit()
    db.refresh(evaluation)
    return evaluation


@router.post("/{evaluation_id}/improvement-plans", status_code=201)
def create_improvement_plan(
    evaluation_id: int,
    payload: ImprovementPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("evaluations:write")),
) -> dict:
    if db.get(PerformanceEvaluation, evaluation_id) is None:
        raise HTTPException(status_code=404, detail="Evaluation not found.")
    plan = ImprovementPlan(
        evaluation_id=evaluation_id,
        status_id=payload.estado_plan_mejora_id,
        commitments=payload.compromisos,
        due_date=payload.fecha_limite,
    )
    db.add(plan)
    db.flush()
    audit(db, current_user, "create", "plan_mejora", plan.id)
    db.commit()
    return {"id": plan.id}
