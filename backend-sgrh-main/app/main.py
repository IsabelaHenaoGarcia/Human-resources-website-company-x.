from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import install_error_handlers
from app.modules.admin.router import router as admin_router
from app.modules.affiliations.router import router as affiliations_router
from app.modules.audit.router import router as audit_router
from app.modules.auth.router import router as auth_router
from app.modules.certificates.router import router as certificates_router
from app.modules.documents.router import router as documents_router
from app.modules.employees.router import router as employees_router
from app.modules.evaluations.router import router as evaluations_router
from app.modules.offboarding.router import router as offboarding_router
from app.modules.payroll.router import router as payroll_router
from app.modules.recruitment.router import router as recruitment_router
from app.modules.reports.router import router as reports_router
from app.modules.training.router import router as training_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="SGRH Backend",
        version="0.1.0",
        description="FastAPI backend for the Human Resources / Human Management System.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_error_handlers(app)

    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(employees_router)
    app.include_router(documents_router)
    app.include_router(recruitment_router)
    app.include_router(affiliations_router)
    app.include_router(payroll_router)
    app.include_router(offboarding_router)
    app.include_router(training_router)
    app.include_router(evaluations_router)
    app.include_router(certificates_router)
    app.include_router(reports_router)
    app.include_router(audit_router)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()

