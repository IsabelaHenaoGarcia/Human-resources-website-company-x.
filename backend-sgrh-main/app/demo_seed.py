from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.core.db import SessionLocal
from app.core.security import hash_password
from app.modules.affiliations.models import Affiliation, AffiliationStatus, AffiliationType
from app.modules.audit.models import AuditLog
from app.modules.auth.models import Role, User, UserStatus
from app.modules.certificates.models import CertificateStatus, CertificateType, EmploymentCertificate
from app.modules.documents.models import DocumentType
from app.modules.employees.models import Employee, EmployeeStatus
from app.modules.evaluations.models import EvaluationStatus, ImprovementPlan, ImprovementPlanStatus, PerformanceEvaluation
from app.modules.offboarding.models import ContractSettlement, ContractSettlementStatus, Offboarding, OffboardingStatus, WithdrawalReason
from app.modules.payroll.models import (
    PayrollNovelty,
    PayrollNoveltyType,
    PayrollPeriod,
    PayrollPeriodStatus,
    PayrollSettlement,
    PayrollSettlementStatus,
)
from app.modules.recruitment.models import Candidate, CandidateStatus, CandidateTest, Contract, ContractStatus, ContractType, Interview, InterviewStatus
from app.modules.training.models import AnnualTrainingPlan, TrainingActivity, TrainingActivityStatus, TrainingActivityType, TrainingAttendance
from app.seed import seed_all

DEMO_PASSWORD = "Demo123!"


def catalog(db: Session, model: type, code: str):
    row = db.scalar(select(model).where(model.code == code))
    if row is None:
        raise RuntimeError(f"Missing catalog {model.__tablename__}.{code}")
    return row


def user(db: Session, username: str, full_name: str, role_code: str) -> User:
    row = db.scalar(select(User).where(User.username == username))
    active = catalog(db, UserStatus, "active")
    role = catalog(db, Role, role_code)
    if row is None:
        row = User(
            username=username,
            password_hash=hash_password(DEMO_PASSWORD),
            full_name=full_name,
            status_id=active.id,
            roles=[role],
        )
        db.add(row)
    else:
        row.full_name = full_name
        row.status_id = active.id
        row.roles = [role]
    db.flush()
    return row


def employee(db: Session, **values) -> Employee:
    row = db.scalar(select(Employee).where(Employee.document_number == values["document_number"]))
    if row is None:
        row = Employee(**values)
        db.add(row)
    else:
        for key, value in values.items():
            setattr(row, key, value)
    db.flush()
    return row


def candidate(db: Session, **values) -> Candidate:
    row = db.scalar(select(Candidate).where(Candidate.document_number == values["document_number"]))
    if row is None:
        row = Candidate(**values)
        db.add(row)
    else:
        for key, value in values.items():
            setattr(row, key, value)
    db.flush()
    return row


def first_or_create(db: Session, model: type, where, values: dict):
    row = db.scalar(select(model).where(*where))
    if row is None:
        row = model(**values)
        db.add(row)
    else:
        for key, value in values.items():
            setattr(row, key, value)
    db.flush()
    return row


def audit_once(db: Session, user_id: int | None, action: str, entity: str, record_id: int | None, detail: str) -> None:
    row = db.scalar(
        select(AuditLog).where(
            AuditLog.user_id == user_id,
            AuditLog.action == action,
            AuditLog.entity == entity,
            AuditLog.record_id == record_id,
            AuditLog.detail == detail,
        )
    )
    if row is None:
        db.add(
            AuditLog(
                user_id=user_id,
                action=action,
                entity=entity,
                record_id=record_id,
                detail=detail,
                event_date=datetime.now(UTC),
            )
        )


def seed_demo(db: Session) -> None:
    seed_all(db)

    admin = db.scalar(select(User).where(User.username == "admin"))
    rrhh = user(db, "rrhh.demo", "Laura Rojas - RRHH", "RRHH")
    manager = user(db, "gerencia.demo", "Carlos Mendoza - Gerencia", "GERENCIA")
    payroll_user = user(db, "nomina.demo", "Sofia Torres - Nomina", "CONTABILIDAD")

    cc = catalog(db, DocumentType, "cc")
    active_employee = catalog(db, EmployeeStatus, "active")
    retired_employee = catalog(db, EmployeeStatus, "retired")

    employees = [
        employee(
            db,
            document_type_id=cc.id,
            employee_status_id=active_employee.id,
            full_name="Ana Maria Gomez",
            document_number="DEMO-EMP-1001",
            birth_date=date(1993, 4, 16),
            email="ana.gomez@example.edu",
            phone="3001112233",
            address="Calle 10 #15-20",
            position="Analista de talento humano",
            hire_date=date(2023, 2, 1),
            base_salary=Decimal("4200000"),
            eps_entity="Sura EPS",
            pension_entity="Proteccion",
            has_beneficiaries=True,
            beneficiary_notes="Conyuge e hijo registrados",
            induction_completed=True,
            latest_evaluation_status="completed",
            latest_evaluation_date=date(2026, 4, 20),
            user_id=rrhh.id,
        ),
        employee(
            db,
            document_type_id=cc.id,
            employee_status_id=active_employee.id,
            full_name="Mateo Rodriguez",
            document_number="DEMO-EMP-1002",
            birth_date=date(1990, 9, 3),
            email="mateo.rodriguez@example.edu",
            phone="3002223344",
            address="Carrera 7 #22-11",
            position="Desarrollador backend",
            hire_date=date(2022, 8, 16),
            base_salary=Decimal("6100000"),
            eps_entity="Nueva EPS",
            pension_entity="Porvenir",
            has_beneficiaries=False,
            beneficiary_notes=None,
            induction_completed=True,
            latest_evaluation_status="completed",
            latest_evaluation_date=date(2026, 3, 18),
            user_id=None,
        ),
        employee(
            db,
            document_type_id=cc.id,
            employee_status_id=active_employee.id,
            full_name="Valentina Perez",
            document_number="DEMO-EMP-1003",
            birth_date=date(1996, 1, 12),
            email="valentina.perez@example.edu",
            phone="3003334455",
            address="Av. Boyaca #40-55",
            position="Coordinadora de nomina",
            hire_date=date(2021, 11, 2),
            base_salary=Decimal("5200000"),
            eps_entity="Compensar EPS",
            pension_entity="Colfondos",
            has_beneficiaries=True,
            beneficiary_notes="Madre beneficiaria",
            induction_completed=True,
            latest_evaluation_status="scheduled",
            latest_evaluation_date=date(2026, 6, 10),
            user_id=payroll_user.id,
        ),
        employee(
            db,
            document_type_id=cc.id,
            employee_status_id=retired_employee.id,
            full_name="Julian Castro",
            document_number="DEMO-EMP-1004",
            birth_date=date(1988, 7, 8),
            email="julian.castro@example.edu",
            phone="3004445566",
            address="Diagonal 45 #18-09",
            position="Auxiliar administrativo",
            hire_date=date(2020, 5, 12),
            base_salary=Decimal("2800000"),
            eps_entity="Sanitas EPS",
            pension_entity="Proteccion",
            has_beneficiaries=False,
            beneficiary_notes=None,
            induction_completed=True,
            latest_evaluation_status="closed",
            latest_evaluation_date=date(2025, 11, 30),
            user_id=None,
        ),
    ]

    hired = catalog(db, CandidateStatus, "hired")
    in_process = catalog(db, CandidateStatus, "in_process")
    draft = catalog(db, CandidateStatus, "draft")
    candidates = [
        candidate(
            db,
            document_type_id=cc.id,
            candidate_status_id=in_process.id,
            full_name="Daniela Ruiz",
            document_number="DEMO-CAN-2001",
            email="daniela.ruiz@example.edu",
            phone="3015551001",
            position_applied="Analista de seleccion",
            interview_result_summary="Buen ajuste cultural y tecnico.",
            references_verified=True,
            background_verified=True,
            occupational_exam_date=date(2026, 5, 18),
            occupational_exam_result="Apto",
            occupational_exam_observations="Sin restricciones.",
        ),
        candidate(
            db,
            document_type_id=cc.id,
            candidate_status_id=draft.id,
            full_name="Nicolas Herrera",
            document_number="DEMO-CAN-2002",
            email="nicolas.herrera@example.edu",
            phone="3015551002",
            position_applied="Soporte TI",
            interview_result_summary="Pendiente entrevista tecnica.",
            references_verified=False,
            background_verified=False,
            occupational_exam_date=None,
            occupational_exam_result=None,
            occupational_exam_observations=None,
        ),
        candidate(
            db,
            document_type_id=cc.id,
            candidate_status_id=hired.id,
            full_name="Paula Martinez",
            document_number="DEMO-CAN-2003",
            email="paula.martinez@example.edu",
            phone="3015551003",
            position_applied="Asistente contable",
            interview_result_summary="Contratada para apoyo de nomina.",
            references_verified=True,
            background_verified=True,
            occupational_exam_date=date(2026, 4, 30),
            occupational_exam_result="Apto",
            occupational_exam_observations="Ingreso autorizado.",
        ),
    ]

    interview_status = catalog(db, InterviewStatus, "scheduled")
    for index, item in enumerate(candidates, start=1):
        first_or_create(
            db,
            Interview,
            [Interview.candidate_id == item.id, Interview.interviewer == "Laura Rojas - RRHH"],
            {
                "candidate_id": item.id,
                "status_id": interview_status.id,
                "scheduled_at": datetime(2026, 6, index + 3, 9, 0, tzinfo=UTC),
                "interviewer": "Laura Rojas - RRHH",
                "result": item.interview_result_summary,
                "observations": "Registro demo para proyecto academico.",
            },
        )
        first_or_create(
            db,
            CandidateTest,
            [CandidateTest.candidate_id == item.id, CandidateTest.test_type == "Prueba tecnica demo"],
            {
                "candidate_id": item.id,
                "test_type": "Prueba tecnica demo",
                "result": "Aprobado" if index != 2 else "Pendiente",
                "observations": "Resultado de ejemplo.",
            },
        )

    contract_type = catalog(db, ContractType, "indefinite")
    active_contract = catalog(db, ContractStatus, "active")
    finished_contract = catalog(db, ContractStatus, "finished")
    contracts = []
    for item in employees:
        contracts.append(
            first_or_create(
                db,
                Contract,
                [Contract.employee_id == item.id, Contract.start_date == item.hire_date],
                {
                    "employee_id": item.id,
                    "contract_type_id": contract_type.id,
                    "contract_status_id": finished_contract.id if item.document_number == "DEMO-EMP-1004" else active_contract.id,
                    "position": item.position,
                    "base_salary": item.base_salary,
                    "start_date": item.hire_date,
                    "end_date": date(2026, 5, 15) if item.document_number == "DEMO-EMP-1004" else None,
                },
            )
        )

    completed_affiliation = catalog(db, AffiliationStatus, "completed")
    for item in employees:
        for type_code, entity in [("eps", item.eps_entity or "EPS Demo"), ("pension", item.pension_entity or "Pension Demo")]:
            affiliation_type = catalog(db, AffiliationType, type_code)
            first_or_create(
                db,
                Affiliation,
                [Affiliation.employee_id == item.id, Affiliation.affiliation_type_id == affiliation_type.id],
                {
                    "employee_id": item.id,
                    "affiliation_type_id": affiliation_type.id,
                    "affiliation_status_id": completed_affiliation.id,
                    "entity": entity,
                    "registration_date": item.hire_date,
                    "observations": "Afiliacion demo cargada para pruebas.",
                },
            )

    approved_period = catalog(db, PayrollPeriodStatus, "approved")
    reviewed_settlement = catalog(db, PayrollSettlementStatus, "reviewed")
    period = first_or_create(
        db,
        PayrollPeriod,
        [PayrollPeriod.start_date == date(2026, 5, 1), PayrollPeriod.end_date == date(2026, 5, 31)],
        {
            "status_id": approved_period.id,
            "name": "Nomina Mayo 2026 Demo",
            "start_date": date(2026, 5, 1),
            "end_date": date(2026, 5, 31),
            "approved_by_id": manager.id,
            "approved_at": datetime(2026, 5, 28, 16, 30, tzinfo=UTC),
            "approval_comment": "Periodo aprobado para datos demo.",
        },
    )
    bonus = catalog(db, PayrollNoveltyType, "bonus")
    for item in employees[:3]:
        earnings = Decimal("250000")
        deductions = (item.base_salary * Decimal("0.08")).quantize(Decimal("1"))
        first_or_create(
            db,
            PayrollSettlement,
            [PayrollSettlement.employee_id == item.id, PayrollSettlement.payroll_period_id == period.id],
            {
                "employee_id": item.id,
                "payroll_period_id": period.id,
                "status_id": reviewed_settlement.id,
                "base_salary": item.base_salary,
                "earnings_total": earnings,
                "deductions_total": deductions,
                "net_pay": item.base_salary + earnings - deductions,
                "approved_by_id": manager.id,
                "approved_at": datetime(2026, 5, 29, 10, 0, tzinfo=UTC),
                "approval_comment": "Liquidacion demo revisada.",
            },
        )
        first_or_create(
            db,
            PayrollNovelty,
            [PayrollNovelty.employee_id == item.id, PayrollNovelty.payroll_period_id == period.id, PayrollNovelty.novelty_type_id == bonus.id],
            {
                "employee_id": item.id,
                "payroll_period_id": period.id,
                "novelty_type_id": bonus.id,
                "document_id": None,
                "application_date": date(2026, 5, 20),
                "amount": earnings,
                "hours": None,
                "observations": "Bonificacion demo por cumplimiento.",
            },
        )

    offboarding_status = catalog(db, OffboardingStatus, "completed")
    withdrawal_reason = catalog(db, WithdrawalReason, "resignation")
    offboarding = first_or_create(
        db,
        Offboarding,
        [Offboarding.employee_id == employees[3].id, Offboarding.contract_id == contracts[3].id],
        {
            "employee_id": employees[3].id,
            "contract_id": contracts[3].id,
            "reason_id": withdrawal_reason.id,
            "status_id": offboarding_status.id,
            "withdrawal_date": date(2026, 5, 15),
            "observations": "Retiro voluntario demo.",
            "exit_exam_completed": True,
            "equipment_returned": True,
            "uniforms_returned": True,
            "checklist_observations": "Checklist completo.",
        },
    )
    settlement_status = catalog(db, ContractSettlementStatus, "approved")
    first_or_create(
        db,
        ContractSettlement,
        [ContractSettlement.offboarding_id == offboarding.id],
        {
            "offboarding_id": offboarding.id,
            "status_id": settlement_status.id,
            "vacation": Decimal("620000"),
            "bonus": Decimal("410000"),
            "severance": Decimal("820000"),
            "severance_interest": Decimal("98000"),
            "deductions": Decimal("50000"),
            "total": Decimal("1898000"),
            "observations": "Liquidacion de contrato demo.",
            "approved_by_id": manager.id,
            "approved_at": datetime(2026, 5, 16, 14, 0, tzinfo=UTC),
            "approval_comment": "Aprobada para cierre academico.",
        },
    )

    training_type = catalog(db, TrainingActivityType, "training")
    completed_training = catalog(db, TrainingActivityStatus, "completed")
    for name, day in [("Induccion SGRH Demo", 6), ("Seguridad y salud en el trabajo Demo", 13), ("Proteccion de datos personales Demo", 20)]:
        activity = first_or_create(
            db,
            TrainingActivity,
            [TrainingActivity.name == name],
            {
                "type_id": training_type.id,
                "status_id": completed_training.id,
                "name": name,
                "scheduled_date": date(2026, 5, day),
                "description": "Actividad demo para validar el modulo de capacitacion.",
            },
        )
        for item in employees[:3]:
            first_or_create(
                db,
                TrainingAttendance,
                [TrainingAttendance.training_activity_id == activity.id, TrainingAttendance.employee_id == item.id],
                {
                    "training_activity_id": activity.id,
                    "employee_id": item.id,
                    "attended": True,
                    "observations": "Asistencia demo confirmada.",
                },
            )
    first_or_create(
        db,
        AnnualTrainingPlan,
        [AnnualTrainingPlan.year == 2026],
        {"year": 2026, "description": "Plan anual demo con induccion, SST y proteccion de datos."},
    )

    evaluation_status = catalog(db, EvaluationStatus, "completed")
    plan_status = catalog(db, ImprovementPlanStatus, "open")
    for index, item in enumerate(employees[:3], start=1):
        evaluation = first_or_create(
            db,
            PerformanceEvaluation,
            [PerformanceEvaluation.employee_id == item.id, PerformanceEvaluation.evaluation_type == "Semestral demo"],
            {
                "employee_id": item.id,
                "status_id": evaluation_status.id,
                "evaluation_type": "Semestral demo",
                "evaluation_date": date(2026, 4, 10 + index),
                "score": Decimal(f"4.{index}"),
                "observations": "Evaluacion demo con resultado satisfactorio.",
            },
        )
        first_or_create(
            db,
            ImprovementPlan,
            [ImprovementPlan.evaluation_id == evaluation.id],
            {
                "evaluation_id": evaluation.id,
                "status_id": plan_status.id,
                "commitments": "Mantener seguimiento mensual y documentar avances.",
                "due_date": date(2026, 7, 30),
            },
        )

    certificate_type = catalog(db, CertificateType, "employment")
    certificate_status = catalog(db, CertificateStatus, "generated")
    for item in employees[:3]:
        first_or_create(
            db,
            EmploymentCertificate,
            [EmploymentCertificate.employee_id == item.id, EmploymentCertificate.certificate_type_id == certificate_type.id],
            {
                "employee_id": item.id,
                "certificate_type_id": certificate_type.id,
                "status_id": certificate_status.id,
                "document_id": None,
                "observation": "Certificado laboral demo generado.",
            },
        )

    audit_user_id = admin.id if admin else rrhh.id
    events = [
        (audit_user_id, "login", "usuario", audit_user_id, "Demo SGRH: inicio de sesion administrador."),
        (rrhh.id, "create", "empleado", employees[0].id, "Demo SGRH: creacion de empleado Ana Maria Gomez."),
        (rrhh.id, "update", "candidato", candidates[0].id, "Demo SGRH: validacion de referencias."),
        (payroll_user.id, "settle", "periodo_nomina", period.id, "Demo SGRH: liquidacion de nomina mayo."),
        (manager.id, "approve_payroll", "periodo_nomina", period.id, "Demo SGRH: aprobacion gerencial de nomina."),
        (rrhh.id, "create", "actividad_formativa", None, "Demo SGRH: capacitaciones completadas."),
        (rrhh.id, "create", "evaluacion_desempeno", None, "Demo SGRH: evaluaciones semestrales cargadas."),
        (rrhh.id, "generate_certificate", "certificacion_laboral", None, "Demo SGRH: certificados laborales disponibles."),
        (None, "system_seed", "demo_data", None, "Demo SGRH: datos academicos cargados correctamente."),
    ]
    for user_id, action, entity, record_id, detail in events:
        audit_once(db, user_id, action, entity, record_id, detail)

    db.commit()


if __name__ == "__main__":
    session = SessionLocal()
    try:
        seed_demo(session)
        print("Demo data seeded. Demo users use password:", DEMO_PASSWORD)
    finally:
        session.close()
