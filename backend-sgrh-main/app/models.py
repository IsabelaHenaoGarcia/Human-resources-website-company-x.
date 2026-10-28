"""Compatibility import surface for SQLAlchemy metadata registration.

Domain model definitions live in `app/modules/*/models.py`. Importing this
module loads every mapped class so Alembic can discover the full metadata.
Application code should import models from the owning module.
"""

from app.modules.affiliations.models import Affiliation, AffiliationStatus, AffiliationType
from app.modules.audit.models import AuditLog
from app.modules.auth.models import Permission, Role, RolePermission, User, UserRole, UserStatus
from app.modules.certificates.models import CertificateStatus, CertificateType, EmploymentCertificate
from app.modules.documents.models import (
    AffiliationDocument,
    CandidateDocument,
    ContractDocument,
    ContractSettlementDocument,
    Document,
    DocumentType,
    EmployeeDocument,
    FileType,
    OffboardingDocument,
    SupportDocumentType,
    TrainingActivityDocument,
)
from app.modules.employees.models import Employee, EmployeeStatus
from app.modules.evaluations.models import EvaluationStatus, ImprovementPlan, ImprovementPlanStatus, PerformanceEvaluation
from app.modules.offboarding.models import ContractSettlement, ContractSettlementStatus, Offboarding, OffboardingStatus, WithdrawalReason
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
from app.modules.recruitment.models import (
    Candidate,
    CandidateStatus,
    CandidateTest,
    Contract,
    ContractStatus,
    ContractType,
    Interview,
    InterviewStatus,
)
from app.modules.training.models import AnnualTrainingPlan, TrainingActivity, TrainingActivityStatus, TrainingActivityType, TrainingAttendance

__all__ = [
    "Affiliation",
    "AffiliationDocument",
    "AffiliationStatus",
    "AffiliationType",
    "AnnualTrainingPlan",
    "AuditLog",
    "Candidate",
    "CandidateDocument",
    "CandidateStatus",
    "CandidateTest",
    "CertificateStatus",
    "CertificateType",
    "Contract",
    "ContractDocument",
    "ContractSettlement",
    "ContractSettlementDocument",
    "ContractSettlementStatus",
    "ContractStatus",
    "ContractType",
    "ContributionsDetail",
    "ContributionsForm",
    "ContributionsStatus",
    "Document",
    "DocumentType",
    "Employee",
    "EmployeeDocument",
    "EmployeeStatus",
    "EmploymentCertificate",
    "EvaluationStatus",
    "FileType",
    "ImprovementPlan",
    "ImprovementPlanStatus",
    "Interview",
    "InterviewStatus",
    "Offboarding",
    "OffboardingDocument",
    "OffboardingStatus",
    "PaySlip",
    "PayrollNovelty",
    "PayrollNoveltyType",
    "PayrollPeriod",
    "PayrollPeriodStatus",
    "PayrollSettlement",
    "PayrollSettlementStatus",
    "Permission",
    "PerformanceEvaluation",
    "Role",
    "RolePermission",
    "SupportDocumentType",
    "TrainingActivity",
    "TrainingActivityDocument",
    "TrainingActivityStatus",
    "TrainingActivityType",
    "TrainingAttendance",
    "User",
    "UserRole",
    "UserStatus",
    "WithdrawalReason",
]

