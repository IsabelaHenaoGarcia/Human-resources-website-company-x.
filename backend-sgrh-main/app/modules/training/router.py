from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.rbac import require_any_permission, require_permission
from app.modules.auth.models import User
from app.modules.employees.models import Employee
from app.modules.training.models import AnnualTrainingPlan, TrainingActivity, TrainingAttendance
from app.modules.training.schemas import (
    AnnualTrainingPlanCreate,
    TrainingActivityCreate,
    TrainingActivityRead,
    TrainingAttendanceCreate,
)
from app.services import audit

router = APIRouter(prefix="/training", tags=["training"])


@router.get("/activities", response_model=list[TrainingActivityRead])
def list_activities(
    db: Session = Depends(get_db),
    _: User = Depends(require_any_permission("training:read", "reports:read")),
) -> list[TrainingActivity]:
    return list(db.scalars(select(TrainingActivity).order_by(TrainingActivity.scheduled_date.desc())).all())


@router.post("/activities", response_model=TrainingActivityRead, status_code=201)
def create_activity(
    payload: TrainingActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("training:write")),
) -> TrainingActivity:
    activity = TrainingActivity(**payload.model_dump())
    db.add(activity)
    db.flush()
    audit(db, current_user, "create", "actividad_formativa", activity.id)
    db.commit()
    db.refresh(activity)
    return activity


@router.post("/activities/{activity_id}/attendances", status_code=201)
def create_attendance(
    activity_id: int,
    payload: TrainingAttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("training:write")),
) -> dict:
    if db.get(TrainingActivity, activity_id) is None:
        raise HTTPException(status_code=404, detail="Training activity not found.")
    if db.get(Employee, payload.empleado_id) is None:
        raise HTTPException(status_code=404, detail="Employee not found.")
    attendance = TrainingAttendance(
        training_activity_id=activity_id,
        employee_id=payload.empleado_id,
        attended=payload.asistio,
        observations=payload.observaciones,
    )
    db.add(attendance)
    db.flush()
    audit(db, current_user, "create", "asistencia_actividad_formativa", attendance.id)
    db.commit()
    return {"id": attendance.id}


@router.get("/annual-plan")
def list_annual_plans(
    db: Session = Depends(get_db),
    _: User = Depends(require_any_permission("training:read", "reports:read")),
) -> list[dict]:
    plans = db.scalars(select(AnnualTrainingPlan).order_by(AnnualTrainingPlan.year.desc())).all()
    return [{"id": plan.id, "year": plan.year, "description": plan.description} for plan in plans]


@router.post("/annual-plan", status_code=201)
def create_annual_plan(
    payload: AnnualTrainingPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("training:write")),
) -> dict:
    plan = AnnualTrainingPlan(**payload.model_dump())
    db.add(plan)
    db.flush()
    audit(db, current_user, "create", "plan_anual_capacitacion", plan.id)
    db.commit()
    return {"id": plan.id, "year": plan.year, "description": plan.description}
