from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.affiliations.models import AffiliationStatus, AffiliationType
from app.modules.auth.models import Permission, Role
from app.modules.certificates.models import CertificateStatus, CertificateType
from app.modules.documents.models import DocumentType, FileType, SupportDocumentType
from app.modules.employees.models import EmployeeStatus
from app.modules.evaluations.models import EvaluationStatus, ImprovementPlanStatus
from app.modules.offboarding.models import ContractSettlementStatus, OffboardingStatus, WithdrawalReason
from app.modules.payroll.models import PayrollNoveltyType, PayrollPeriodStatus
from app.modules.recruitment.models import CandidateStatus, ContractStatus, ContractType, InterviewStatus
from app.modules.training.models import TrainingActivityStatus, TrainingActivityType


def catalog_id(db: Session, model: type, code: str) -> int:
    row = db.scalar(select(model).where(model.code == code))
    assert row is not None, f"Missing catalog {model.__name__}:{code}"
    return row.id


def assert_ok(response, expected: int = 200):
    assert response.status_code == expected, response.text
    return response.json() if response.content else None


def test_public_docs_and_health(client: TestClient):
    assert client.get("/health").status_code == 200
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200
    assert client.get("/docs/oauth2-redirect").status_code == 200
    openapi = assert_ok(client.get("/openapi.json"))
    assert openapi["info"]["title"] == "SGRH Backend"


def test_auth_and_admin_endpoints(client: TestClient, auth_headers: dict[str, str]):
    assert client.post("/auth/login", json={"username": "admin", "password": "wrong"}).status_code == 401
    me = assert_ok(client.get("/auth/me", headers=auth_headers))
    assert me["username"] == "admin"
    assert_ok(client.get("/admin/users", headers=auth_headers))
    assert_ok(client.get("/admin/roles", headers=auth_headers))
    assert_ok(client.get("/admin/permissions", headers=auth_headers))
    created = assert_ok(
        client.post(
            "/admin/users",
            json={
                "username": "rrhh",
                "password": "Password123!",
                "full_name": "HR User",
                "role_codes": ["RRHH"],
            },
            headers=auth_headers,
        ),
        201,
    )
    updated = assert_ok(
        client.put(
            f"/admin/users/{created['id']}",
            json={"full_name": "HR Updated", "active": True, "role_codes": ["RRHH", "GERENCIA"]},
            headers=auth_headers,
        )
    )
    assert updated["full_name"] == "HR Updated"
    assert client.post("/auth/logout", headers=auth_headers).status_code == 204


def test_employee_recruitment_documents_and_affiliations(db_session: Session, client: TestClient, auth_headers: dict[str, str]):
    cc = catalog_id(db_session, DocumentType, "cc")
    active = catalog_id(db_session, EmployeeStatus, "active")
    on_leave = catalog_id(db_session, EmployeeStatus, "on_leave")
    candidate_draft = catalog_id(db_session, CandidateStatus, "draft")
    candidate_in_process = catalog_id(db_session, CandidateStatus, "in_process")
    interview_scheduled = catalog_id(db_session, InterviewStatus, "scheduled")
    contract_type = catalog_id(db_session, ContractType, "indefinite")
    contract_status = catalog_id(db_session, ContractStatus, "draft")
    file_type_pdf = catalog_id(db_session, FileType, "pdf")
    support_cv = catalog_id(db_session, SupportDocumentType, "cv")
    support_contract = catalog_id(db_session, SupportDocumentType, "contract")
    support_affiliation = catalog_id(db_session, SupportDocumentType, "affiliation_proof")
    affiliation_type = catalog_id(db_session, AffiliationType, "eps")
    affiliation_pending = catalog_id(db_session, AffiliationStatus, "pending")
    affiliation_in_progress = catalog_id(db_session, AffiliationStatus, "in_progress")

    employee = assert_ok(
        client.post(
            "/employees",
            json={
                "document_type_id": cc,
                "employee_status_id": active,
                "full_name": "Alice Employee",
                "document_number": "10001",
                "position": "Analyst",
                "hire_date": "2026-01-15",
                "base_salary": "2500000",
            },
            headers=auth_headers,
        ),
        201,
    )
    employee_id = employee["id"]
    assert_ok(client.get("/employees", headers=auth_headers))
    assert_ok(client.get(f"/employees/{employee_id}", headers=auth_headers))
    assert_ok(client.put(f"/employees/{employee_id}", json={"employee_status_id": on_leave}, headers=auth_headers))

    candidate = assert_ok(
        client.post(
            "/recruitment/candidates",
            json={
                "document_type_id": cc,
                "candidate_status_id": candidate_draft,
                "full_name": "Bob Candidate",
                "document_number": "20001",
                "position_applied": "Developer",
            },
            headers=auth_headers,
        ),
        201,
    )
    candidate_id = candidate["id"]
    duplicate = client.post(
        "/employees",
        json={
            "document_type_id": cc,
            "employee_status_id": active,
            "full_name": "Duplicate",
            "document_number": "20001",
            "position": "Analyst",
            "hire_date": "2026-01-15",
        },
        headers=auth_headers,
    )
    assert duplicate.status_code == 409
    assert_ok(client.get("/recruitment/candidates", headers=auth_headers))
    assert_ok(client.get(f"/recruitment/candidates/{candidate_id}", headers=auth_headers))
    assert_ok(
        client.put(
            f"/recruitment/candidates/{candidate_id}",
            json={"candidate_status_id": candidate_in_process},
            headers=auth_headers,
        )
    )
    assert_ok(
        client.post(
            f"/recruitment/candidates/{candidate_id}/verifications",
            json={"referencias_verificadas": True, "antecedentes_verificados": True},
            headers=auth_headers,
        )
    )
    assert_ok(
        client.post(
            f"/recruitment/candidates/{candidate_id}/tests",
            json={"tipo_prueba": "technical", "resultado": "approved"},
            headers=auth_headers,
        ),
        201,
    )
    assert_ok(
        client.post(
            f"/recruitment/candidates/{candidate_id}/occupational-exam",
            json={"fecha": "2026-02-01", "resultado": "approved"},
            headers=auth_headers,
        )
    )
    assert_ok(
        client.post(
            "/recruitment/interviews",
            json={
                "candidato_id": candidate_id,
                "fecha_hora": "2026-02-02T09:00:00Z",
                "entrevistador": "HR",
                "estado_entrevista_id": interview_scheduled,
            },
            headers=auth_headers,
        ),
        201,
    )
    contract = assert_ok(
        client.post(
            "/recruitment/contracts",
            json={
                "empleado_id": employee_id,
                "tipo_contrato_id": contract_type,
                "cargo": "Analyst",
                "salario_base": "2500000",
                "fecha_inicio": "2026-01-15",
                "estado_contrato_id": contract_status,
            },
            headers=auth_headers,
        ),
        201,
    )
    contract_id = contract["id"]
    assert_ok(client.get("/recruitment/contracts", headers=auth_headers))

    bad_upload = client.post(
        "/documents/upload",
        data={"tipo_archivo_id": file_type_pdf},
        files={"file": ("malware.exe", b"nope", "application/octet-stream")},
        headers=auth_headers,
    )
    assert bad_upload.status_code == 400
    document = assert_ok(
        client.post(
            "/documents/upload",
            data={"tipo_archivo_id": file_type_pdf, "nombre_archivo": "support.pdf"},
            files={"file": ("support.pdf", b"%PDF-1.4\n%%EOF", "application/pdf")},
            headers=auth_headers,
        ),
        201,
    )
    document_id = document["id"]
    assert client.get(f"/documents/{document_id}/download", headers=auth_headers).status_code == 200
    assert_ok(
        client.post(
            f"/employees/{employee_id}/documents",
            json={"document_id": document_id, "support_document_type_id": support_cv},
            headers=auth_headers,
        ),
        201,
    )
    assert_ok(
        client.post(
            f"/candidates/{candidate_id}/documents",
            json={"document_id": document_id, "support_document_type_id": support_cv},
            headers=auth_headers,
        ),
        201,
    )
    assert_ok(
        client.post(
            f"/contracts/{contract_id}/documents",
            json={"document_id": document_id, "support_document_type_id": support_contract},
            headers=auth_headers,
        ),
        201,
    )

    affiliation = assert_ok(
        client.post(
            "/affiliations",
            json={
                "empleado_id": employee_id,
                "tipo_afiliacion_id": affiliation_type,
                "entidad": "EPS Test",
                "fecha_registro": "2026-01-16",
                "estado_afiliacion_id": affiliation_pending,
            },
            headers=auth_headers,
        ),
        201,
    )
    affiliation_id = affiliation["id"]
    assert_ok(client.get("/affiliations", headers=auth_headers))
    assert_ok(
        client.put(
            f"/affiliations/{affiliation_id}",
            json={"estado_afiliacion_id": affiliation_in_progress},
            headers=auth_headers,
        )
    )
    assert_ok(
        client.post(
            f"/affiliations/{affiliation_id}/documents",
            json={"document_id": document_id, "support_document_type_id": support_affiliation},
            headers=auth_headers,
        ),
        201,
    )


def test_payroll_offboarding_training_evaluations_certificates_reports_and_audit(
    db_session: Session, client: TestClient, auth_headers: dict[str, str]
):
    cc = catalog_id(db_session, DocumentType, "cc")
    employee_status = catalog_id(db_session, EmployeeStatus, "active")
    contract_type = catalog_id(db_session, ContractType, "indefinite")
    contract_status = catalog_id(db_session, ContractStatus, "draft")
    payroll_draft = catalog_id(db_session, PayrollPeriodStatus, "draft")
    withdrawal_reason = catalog_id(db_session, WithdrawalReason, "resignation")
    offboarding_draft = catalog_id(db_session, OffboardingStatus, "draft")
    settlement_generated = catalog_id(db_session, ContractSettlementStatus, "generated")
    training_type = catalog_id(db_session, TrainingActivityType, "training")
    training_status = catalog_id(db_session, TrainingActivityStatus, "scheduled")
    evaluation_status = catalog_id(db_session, EvaluationStatus, "scheduled")
    improvement_status = catalog_id(db_session, ImprovementPlanStatus, "open")
    certificate_type = catalog_id(db_session, CertificateType, "employment")
    certificate_status = catalog_id(db_session, CertificateStatus, "requested")
    support_settlement = catalog_id(db_session, SupportDocumentType, "contract_settlement")

    employee = assert_ok(
        client.post(
            "/employees",
            json={
                "document_type_id": cc,
                "employee_status_id": employee_status,
                "full_name": "Carol Payroll",
                "document_number": "30001",
                "position": "Accountant",
                "hire_date": "2026-01-01",
                "base_salary": "3000000",
            },
            headers=auth_headers,
        ),
        201,
    )
    employee_id = employee["id"]
    contract = assert_ok(
        client.post(
            "/recruitment/contracts",
            json={
                "empleado_id": employee_id,
                "tipo_contrato_id": contract_type,
                "cargo": "Accountant",
                "salario_base": "3000000",
                "fecha_inicio": "2026-01-01",
                "estado_contrato_id": contract_status,
            },
            headers=auth_headers,
        ),
        201,
    )
    contract_id = contract["id"]

    period = assert_ok(
        client.post(
            "/payroll/periods",
            json={"name": "2026-01A", "start_date": "2026-01-01", "end_date": "2026-01-15", "status_id": payroll_draft},
            headers=auth_headers,
        ),
        201,
    )
    period_id = period["id"]
    assert_ok(client.get("/payroll/periods", headers=auth_headers))
    assert_ok(
        client.post(
            f"/payroll/periods/{period_id}/novelties",
            json={
                "empleado_id": employee_id,
                "tipo_novedad_codigo": "bonus",
                "fecha_aplicacion": "2026-01-10",
                "valor": "100000",
            },
            headers=auth_headers,
        ),
        201,
    )
    settlements = assert_ok(client.post(f"/payroll/periods/{period_id}/settle", headers=auth_headers))
    settlement_id = settlements[0]["id"]
    assert_ok(client.post(f"/payroll/periods/{period_id}/review", json={"aprobado_por_gerencia": True}, headers=auth_headers))
    assert_ok(client.get("/payroll/settlements", headers=auth_headers))
    assert_ok(client.get(f"/payroll/settlements/{settlement_id}", headers=auth_headers))
    payroll_report_document = assert_ok(client.get(f"/payroll/periods/{period_id}/general-report", headers=auth_headers))
    assert_ok(client.post(f"/payroll/settlements/{settlement_id}/pay-slip", headers=auth_headers), 201)
    assert_ok(client.post(f"/payroll/periods/{period_id}/contributions", headers=auth_headers), 201)
    assert_ok(client.post(f"/payroll/periods/{period_id}/contributions/export", headers=auth_headers), 201)

    offboarding = assert_ok(
        client.post(
            "/offboarding",
            json={
                "empleado_id": employee_id,
                "contrato_id": contract_id,
                "fecha_retiro": "2026-02-01",
                "motivo_retiro_id": withdrawal_reason,
                "estado_retiro_id": offboarding_draft,
            },
            headers=auth_headers,
        ),
        201,
    )
    offboarding_id = offboarding["id"]
    assert_ok(client.get("/offboarding", headers=auth_headers))
    assert_ok(
        client.post(
            f"/offboarding/{offboarding_id}/exit-checklist",
            json={"examen_retiro_realizado": True, "implementos_entregados": True, "dotacion_entregada": True},
            headers=auth_headers,
        )
    )
    settlement = assert_ok(
        client.post(
            f"/offboarding/{offboarding_id}/contract-settlement",
            json={
                "vacaciones": "100000",
                "prima": "100000",
                "cesantias": "100000",
                "intereses_cesantias": "10000",
                "deducciones": "5000",
                "estado_liquidacion_id": settlement_generated,
            },
            headers=auth_headers,
        ),
        201,
    )
    assert settlement["total"] == "305000.00"
    assert_ok(
        client.post(
            f"/offboarding/{offboarding_id}/contract-settlement/approve",
            json={"observacion": "approved"},
            headers=auth_headers,
        )
    )
    assert_ok(
        client.post(
            f"/offboarding/{offboarding_id}/documents",
            json={"document_id": payroll_report_document["id"], "support_document_type_id": support_settlement},
            headers=auth_headers,
        ),
        201,
    )
    generated_doc = db_session.scalar(select(SupportDocumentType).where(SupportDocumentType.id == support_settlement))
    assert generated_doc is not None

    activity = assert_ok(
        client.post(
            "/training/activities",
            json={
                "type_id": training_type,
                "status_id": training_status,
                "name": "Security training",
                "scheduled_date": "2026-03-01",
            },
            headers=auth_headers,
        ),
        201,
    )
    assert_ok(client.get("/training/activities", headers=auth_headers))
    assert_ok(
        client.post(
            f"/training/activities/{activity['id']}/attendances",
            json={"empleado_id": employee_id, "asistio": True},
            headers=auth_headers,
        ),
        201,
    )
    assert_ok(client.post("/training/annual-plan", json={"year": 2026, "description": "Plan"}, headers=auth_headers), 201)
    assert_ok(client.get("/training/annual-plan", headers=auth_headers))

    evaluation = assert_ok(
        client.post(
            "/evaluations",
            json={
                "empleado_id": employee_id,
                "estado_evaluacion_id": evaluation_status,
                "tipo_evaluacion": "annual",
                "fecha_evaluacion": "2026-04-01",
                "puntaje": "4.50",
            },
            headers=auth_headers,
        ),
        201,
    )
    assert_ok(client.get("/evaluations", headers=auth_headers))
    assert_ok(
        client.post(
            f"/evaluations/{evaluation['id']}/improvement-plans",
            json={"estado_plan_mejora_id": improvement_status, "compromisos": "Improve process"},
            headers=auth_headers,
        ),
        201,
    )

    certificate = assert_ok(
        client.post(
            "/certificates",
            json={
                "empleado_id": employee_id,
                "tipo_certificacion_id": certificate_type,
                "estado_certificacion_id": certificate_status,
            },
            headers=auth_headers,
        ),
        201,
    )
    assert_ok(client.get("/certificates", headers=auth_headers))
    assert_ok(client.post(f"/certificates/{certificate['id']}/generate", headers=auth_headers), 201)

    for path in [
        "/reports/employees",
        f"/reports/employees/{employee_id}/history",
        "/reports/recruitment",
        "/reports/affiliations",
        "/reports/payroll",
        "/reports/offboarding",
        "/reports/training",
        "/reports/evaluations",
        "/reports/certificates",
        "/audit",
    ]:
        assert_ok(client.get(path, headers=auth_headers))


def test_seeded_catalogs_and_rbac(db_session: Session):
    assert db_session.scalar(select(Role).where(Role.code == "ADMIN")) is not None
    assert db_session.scalar(select(Permission).where(Permission.code == "employees:write")) is not None
    assert db_session.scalar(select(PayrollNoveltyType).where(PayrollNoveltyType.code == "commission")) is not None
