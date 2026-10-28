"""Compatibility import surface for Pydantic schemas.

Domain schemas live beside their routers in `app/modules/*/schemas.py`.
Application code should import schemas from the owning module.
"""

from app.modules.affiliations.schemas import AffiliationCreate, AffiliationRead, AffiliationUpdate
from app.modules.audit.schemas import AuditRead
from app.modules.auth.schemas import LoginRequest, LoginResponse, UserCreate, UserRead, UserUpdate
from app.modules.certificates.schemas import CertificateCreate, CertificateRead
from app.modules.documents.schemas import DocumentLinkCreate, DocumentRead
from app.modules.employees.schemas import EmployeeCreate, EmployeeRead, EmployeeUpdate
from app.modules.evaluations.schemas import EvaluationCreate, EvaluationRead, ImprovementPlanCreate
from app.modules.offboarding.schemas import (
    ContractSettlementCreate,
    ContractSettlementRead,
    ExitChecklistCreate,
    OffboardingCreate,
    OffboardingRead,
)
from app.modules.payroll.schemas import (
    ApprovalRequest,
    PayrollNoveltyCreate,
    PayrollNoveltyRead,
    PayrollPeriodCreate,
    PayrollPeriodRead,
    PayrollSettlementRead,
)
from app.modules.recruitment.schemas import (
    CandidateCreate,
    CandidateRead,
    CandidateTestCreate,
    CandidateUpdate,
    ContractCreate,
    ContractRead,
    InterviewCreate,
    InterviewRead,
    OccupationalExamCreate,
    VerificationCreate,
)
from app.modules.training.schemas import (
    AnnualTrainingPlanCreate,
    TrainingActivityCreate,
    TrainingActivityRead,
    TrainingAttendanceCreate,
)
from app.shared.schemas import CatalogRead

__all__ = [
    "AffiliationCreate",
    "AffiliationRead",
    "AffiliationUpdate",
    "AnnualTrainingPlanCreate",
    "ApprovalRequest",
    "AuditRead",
    "CandidateCreate",
    "CandidateRead",
    "CandidateTestCreate",
    "CandidateUpdate",
    "CatalogRead",
    "CertificateCreate",
    "CertificateRead",
    "ContractCreate",
    "ContractRead",
    "ContractSettlementCreate",
    "ContractSettlementRead",
    "DocumentLinkCreate",
    "DocumentRead",
    "EmployeeCreate",
    "EmployeeRead",
    "EmployeeUpdate",
    "EvaluationCreate",
    "EvaluationRead",
    "ExitChecklistCreate",
    "ImprovementPlanCreate",
    "InterviewCreate",
    "InterviewRead",
    "LoginRequest",
    "LoginResponse",
    "OccupationalExamCreate",
    "OffboardingCreate",
    "OffboardingRead",
    "PayrollNoveltyCreate",
    "PayrollNoveltyRead",
    "PayrollPeriodCreate",
    "PayrollPeriodRead",
    "PayrollSettlementRead",
    "TrainingActivityCreate",
    "TrainingActivityRead",
    "TrainingAttendanceCreate",
    "UserCreate",
    "UserRead",
    "UserUpdate",
    "VerificationCreate",
]

