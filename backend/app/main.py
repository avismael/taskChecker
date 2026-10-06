from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from backend.app.api.admin_teacher_routes import router as admin_teacher_router
from backend.app.api.auth_routes import router as auth_router
from backend.app.api.delivery_routes import router as delivery_router
from backend.app.api.errors import install_error_handlers
from backend.app.api.follow_up_routes import router as follow_up_router
from backend.app.api.organization_routes import router as organization_router
from backend.app.api.page_routes import router as page_router
from backend.app.api.report_routes import router as report_router
from backend.app.api.security import CSRFMiddleware
from backend.app.api.task_routes import router as task_router
from backend.app.config import get_settings
from backend.app.observability.logging import CorrelationMiddleware
from backend.app.persistence import models  # noqa: F401
from backend.app.persistence.base import Base
from backend.app.persistence.session import engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    Path("backend/.data").mkdir(parents=True, exist_ok=True)
    app = FastAPI(title="TaskChecker", version="0.1.0", debug=settings.debug, lifespan=lifespan)
    app.add_middleware(CSRFMiddleware)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret,
        https_only=settings.session_https_only,
        max_age=settings.session_max_age_seconds,
    )
    app.add_middleware(CorrelationMiddleware)
    install_error_handlers(app)
    app.include_router(auth_router)
    app.include_router(admin_teacher_router)
    app.include_router(organization_router)
    app.include_router(page_router)
    app.include_router(task_router)
    app.include_router(delivery_router)
    app.include_router(follow_up_router)
    app.include_router(report_router)
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
