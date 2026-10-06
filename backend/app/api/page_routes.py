from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="frontend/templates")


def _account_role_label(role: str | None) -> str:
    return {
        "teacher": "Docente",
        "administrator": "Administración",
    }.get(role or "", "")


def render(request: Request, template: str, title: str, **context):
    return templates.TemplateResponse(
        request=request,
        name=template,
        context={
            "title": title,
            "authenticated": bool(request.session.get("account_id")),
            "csrf_token": request.session.get("csrf_token", ""),
            "account_email": request.session.get("account_email", ""),
            "account_role_label": _account_role_label(request.session.get("account_role")),
            **context,
        },
    )


@router.get("/")
def home(request: Request):
    destination = "/workspace" if request.session.get("account_id") else "/login"
    return RedirectResponse(destination, status_code=303)


@router.get("/login")
def login_page(request: Request):
    return render(request, "auth/login.html", "Iniciar sesión")


@router.get("/register")
def register_page(request: Request):
    return render(request, "auth/register.html", "Crear espacio de trabajo")


@router.get("/recovery")
def recovery_page(request: Request):
    return render(request, "auth/recovery.html", "Recuperar acceso")


@router.get("/inactive-account")
def inactive_account_page(request: Request):
    return render(request, "auth/inactive.html", "Cuenta no disponible")


@router.get("/workspace")
def workspace_page(request: Request):
    if not request.session.get("account_id"):
        return RedirectResponse("/login", status_code=303)
    return render(request, "workspace.html", "Resumen", eyebrow="Hoy", heading="Una forma más sencilla de seguir cada entrega")


@router.get("/organization")
def organization_page(request: Request):
    if not request.session.get("account_id"):
        return RedirectResponse("/login", status_code=303)
    return render(request, "organization/index.html", "Estudiantes")


@router.get("/tasks")
def tasks_page(request: Request):
    if not request.session.get("account_id"):
        return RedirectResponse("/login", status_code=303)
    return render(request, "tasks/index.html", "Tareas")


@router.get("/follow-up")
def follow_up_page(request: Request):
    if not request.session.get("account_id"):
        return RedirectResponse("/login", status_code=303)
    return render(request, "follow-up/index.html", "Seguimiento")


@router.get("/students/{student_id}")
def student_profile_page(request: Request, student_id: UUID):
    if not request.session.get("account_id"):
        return RedirectResponse("/login", status_code=303)
    return render(
        request,
        "follow-up/profile.html",
        "Perfil del estudiante",
        student_id=str(student_id),
    )


@router.get("/reports")
def reports_page(request: Request):
    if not request.session.get("account_id"):
        return RedirectResponse("/login", status_code=303)
    return render(request, "reports/index.html", "Informes")
