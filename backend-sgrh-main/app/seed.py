from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.modules.affiliations.models import AffiliationStatus, AffiliationType
from app.modules.auth.models import Permission, Role, User, UserStatus
from app.modules.certificates.models import CertificateStatus, CertificateType
from app.modules.documents.models import DocumentType, FileType, SupportDocumentType
from app.modules.employees.models import EmployeeStatus
from app.modules.evaluations.models import EvaluationStatus, ImprovementPlanStatus
from app.modules.offboarding.models import ContractSettlementStatus, OffboardingStatus, WithdrawalReason
from app.modules.payroll.models import (
    ContributionsStatus,
    PayrollNoveltyType,
    PayrollPeriodStatus,
    PayrollSettlementStatus,
)
from app.modules.recruitment.models import CandidateStatus, ContractStatus, ContractType, InterviewStatus
from app.modules.training.models import TrainingActivityStatus, TrainingActivityType


def upsert_catalog(db: Session, model: type, code: str, name: str, **extra):
    row = db.scalar(select(model).where(model.code == code))
    if row is None:
        row = model(code=code, name=name, active=True, **extra)
        db.add(row)
        db.flush()
    else:
        row.name = name
        row.active = True
        for key, value in extra.items():
            setattr(row, key, value)
    return row


def seed_catalogs(db: Session) -> None:
    for code, name in [("active", "Active"), ("inactive", "Inactive")]:
        upsert_catalog(db, UserStatus, code, name)
    for code, name in [("cc", "Cedula de ciudadania"), ("ce", "Cedula de extranjeria"), ("passport", "Passport")]:
        upsert_catalog(db, DocumentType, code, name)
    for code in ["pdf", "jpg", "jpeg", "png", "csv"]:
        upsert_catalog(db, FileType, code, code.upper())
    for code, name in [
        ("cv", "CV / hoja de vida"),
        ("id_copy", "ID copy"),
        ("military_booklet", "Military booklet"),
        ("education_certificate", "Education certificate"),
        ("training_certificate", "Training certificate"),
        ("work_experience_letter", "Work experience letter"),
        ("eps_certificate", "EPS certificate"),
        ("pension_certificate", "Pension certificate"),
        ("beneficiary_support", "Beneficiary support document"),
        ("occupational_exam_result", "Occupational exam result"),
        ("contract", "Contract"),
        ("affiliation_proof", "Affiliation proof"),
        ("payroll_report_export", "Payroll report export"),
        ("pay_slip", "Pay slip"),
        ("contract_settlement", "Contract settlement"),
        ("withdrawal_letter", "Severance/withdrawal letter"),
        ("employment_certificate", "Employment certificate"),
        ("induction_record", "Induction record"),
        ("training_attendance_evidence", "Training attendance evidence"),
    ]:
        upsert_catalog(db, SupportDocumentType, code, name)
    for code in ["draft", "in_process", "approved", "rejected", "hired"]:
        upsert_catalog(db, CandidateStatus, code, code.replace("_", " ").title())
    for code in ["active", "inactive", "on_leave", "retired"]:
        upsert_catalog(db, EmployeeStatus, code, code.replace("_", " ").title())
    for code in ["draft", "active", "finished", "cancelled"]:
        upsert_catalog(db, ContractStatus, code, code.replace("_", " ").title())
    for code in ["pending", "in_progress", "completed", "rejected"]:
        upsert_catalog(db, AffiliationStatus, code, code.replace("_", " ").title())
    for code in ["draft", "in_review", "approved", "closed"]:
        upsert_catalog(db, PayrollPeriodStatus, code, code.replace("_", " ").title())
    for code in ["generated", "reviewed", "approved"]:
        upsert_catalog(db, PayrollSettlementStatus, code, code.replace("_", " ").title())
    for code in ["generated", "reviewed", "exported"]:
        upsert_catalog(db, ContributionsStatus, code, code.replace("_", " ").title())
    for code in ["draft", "in_process", "completed"]:
        upsert_catalog(db, OffboardingStatus, code, code.replace("_", " ").title())
    for code in ["generated", "reviewed", "approved", "paid"]:
        upsert_catalog(db, ContractSettlementStatus, code, code.replace("_", " ").title())
    for code in ["requested", "generated", "delivered"]:
        upsert_catalog(db, CertificateStatus, code, code.replace("_", " ").title())
    for code in ["scheduled", "completed", "closed"]:
        upsert_catalog(db, EvaluationStatus, code, code.replace("_", " ").title())
    for code in ["open", "in_progress", "closed"]:
        upsert_catalog(db, ImprovementPlanStatus, code, code.replace("_", " ").title())
    for code in ["scheduled", "completed", "cancelled"]:
        upsert_catalog(db, InterviewStatus, code, code.replace("_", " ").title())
    for code, name in [("fixed_term", "Fixed term"), ("indefinite", "Indefinite"), ("temporary_agency", "Temporary agency")]:
        upsert_catalog(db, ContractType, code, name)
    for code, name in [("eps", "EPS"), ("arl", "ARL"), ("pension", "Pension"), ("compensation_fund", "Compensation fund")]:
        upsert_catalog(db, AffiliationType, code, name)
    for code, name in [("resignation", "Resignation"), ("termination", "Termination"), ("fixed_term_non_renewal", "Fixed-term non-renewal")]:
        upsert_catalog(db, WithdrawalReason, code, name)
    for code, name in [("induction", "Induction"), ("training", "Training"), ("reinduction", "Reinduction")]:
        upsert_catalog(db, TrainingActivityType, code, name)
    for code in ["scheduled", "completed", "cancelled"]:
        upsert_catalog(db, TrainingActivityStatus, code, code.replace("_", " ").title())
    for code, name in [("employment", "Employment certificate"), ("salary", "Salary certificate")]:
        upsert_catalog(db, CertificateType, code, name)
    for code, name, effect in [
        ("commission", "Commission", "earning"),
        ("bonus", "Bonus", "earning"),
        ("mobility_allowance", "Mobility allowance", "earning"),
        ("overtime", "Overtime", "earning"),
        ("night_surcharge", "Night surcharge", "earning"),
        ("incapacity", "Incapacity", "manual_adjustment"),
        ("employee_fund_deduction", "Employee fund deduction", "deduction"),
        ("authorized_deduction", "Authorized deduction", "deduction"),
    ]:
        upsert_catalog(db, PayrollNoveltyType, code, name, calculation_effect=effect)


def seed_rbac(db: Session) -> None:
    permissions = [
        "*",
        "admin:users",
        "admin:roles",
        "employees:read",
        "employees:write",
        "recruitment:read",
        "recruitment:write",
        "affiliations:read",
        "affiliations:write",
        "documents:read",
        "documents:write",
        "payroll:read",
        "payroll:write",
        "payroll:approve",
        "offboarding:read",
        "offboarding:write",
        "contract_settlements:approve",
        "training:read",
        "training:write",
        "evaluations:read",
        "evaluations:write",
        "certificates:read",
        "certificates:write",
        "reports:read",
        "audit:read",
    ]
    permission_map = {code: upsert_catalog(db, Permission, code, code) for code in permissions}
    role_permissions = {
        "ADMIN": ["*"],
        "RRHH": [
            "employees:read",
            "employees:write",
            "recruitment:read",
            "recruitment:write",
            "affiliations:read",
            "affiliations:write",
            "documents:read",
            "documents:write",
            "offboarding:read",
            "offboarding:write",
            "training:read",
            "training:write",
            "evaluations:read",
            "evaluations:write",
            "certificates:read",
            "certificates:write",
            "reports:read",
        ],
        "CONTABILIDAD": [
            "employees:read",
            "recruitment:read",
            "documents:read",
            "documents:write",
            "payroll:read",
            "payroll:write",
            "offboarding:read",
            "contract_settlements:approve",
            "reports:read",
        ],
        "GERENCIA": [
            "employees:read",
            "recruitment:read",
            "affiliations:read",
            "documents:read",
            "payroll:read",
            "payroll:approve",
            "offboarding:read",
            "reports:read",
            "audit:read",
        ],
        "COLABORADOR": [],
    }
    for role_code, role_permission_codes in role_permissions.items():
        role = upsert_catalog(db, Role, role_code, role_code)
        role.permissions = [permission_map[code] for code in role_permission_codes]


def seed_optional_admin(db: Session) -> None:
    if not settings.initial_admin_password:
        return
    if db.scalar(select(User).where(User.username == settings.initial_admin_username)):
        return
    active_status = db.scalar(select(UserStatus).where(UserStatus.code == "active"))
    admin_role = db.scalar(select(Role).where(Role.code == "ADMIN"))
    db.add(
        User(
            username=settings.initial_admin_username,
            password_hash=hash_password(settings.initial_admin_password),
            full_name="System Administrator",
            status_id=active_status.id,
            roles=[admin_role],
        )
    )


def seed_all(db: Session) -> None:
    seed_catalogs(db)
    seed_rbac(db)
    seed_optional_admin(db)
    db.commit()


if __name__ == "__main__":
    from app.core.db import SessionLocal

    session = SessionLocal()
    try:
        seed_all(session)
    finally:
        session.close()
