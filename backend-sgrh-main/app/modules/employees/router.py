from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.rbac import require_any_permission, require_permission
from app.modules.auth.models import User
from app.modules.employees.models import Employee, EmployeeStatus
from app.modules.employees.schemas import EmployeeCreate, EmployeeRead, EmployeeUpdate
from app.services import audit, ensure_unique_identity
from app.shared.repository import paginate
from app.shared.schemas import PaginatedResponse
from app.shared.status import transition_allowed

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=PaginatedResponse[EmployeeRead])
def list_employees(
    q: str | None = None,
    estado_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_any_permission("employees:read", "payroll:read", "reports:read")),
) -> dict:
    query = select(Employee).order_by(Employee.full_name)
    if q:
        like = f"%{q}%"
        query = query.where(or_(Employee.full_name.ilike(like), Employee.document_number.ilike(like)))
    if estado_id:
        query = query.where(Employee.employee_status_id == estado_id)
    items, total = paginate(db, query, page, page_size)
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.post("", response_model=EmployeeRead, status_code=201)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("employees:write")),
) -> Employee:
    ensure_unique_identity(db, payload.document_type_id, payload.document_number)
    employee = Employee(**payload.model_dump())
    db.add(employee)
    db.flush()
    audit(db, current_user, "create", "empleado", employee.id)
    db.commit()
    db.refresh(employee)
    return employee


@router.get("/{employee_id}", response_model=EmployeeRead)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_any_permission("employees:read", "payroll:read", "reports:read")),
) -> Employee:
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found.")
    return employee


@router.put("/{employee_id}", response_model=EmployeeRead)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("employees:write")),
) -> Employee:
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found.")
    update_data = payload.model_dump(exclude_unset=True)
    doc_type = update_data.get("document_type_id", employee.document_type_id)
    doc_number = update_data.get("document_number", employee.document_number)
    if "document_type_id" in update_data or "document_number" in update_data:
        ensure_unique_identity(db, doc_type, doc_number, employee_id=employee.id)
    if "employee_status_id" in update_data:
        target = db.get(EmployeeStatus, update_data["employee_status_id"])
        if target and not transition_allowed("employee", employee.status.code, target.code):
            raise HTTPException(status_code=400, detail="Invalid employee status transition.")
    for key, value in update_data.items():
        setattr(employee, key, value)
    audit(db, current_user, "update", "empleado", employee.id)
    db.commit()
    db.refresh(employee)
    return employee
