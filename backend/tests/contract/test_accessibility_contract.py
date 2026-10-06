from pathlib import Path

TEMPLATE_ROOT = Path("frontend/templates")
STATIC_ROOT = Path("frontend/static")


def test_primary_pages_have_heading_and_labeled_form_controls():
    pages = (
        TEMPLATE_ROOT / "auth/login.html",
        TEMPLATE_ROOT / "auth/register.html",
        TEMPLATE_ROOT / "auth/recovery.html",
        TEMPLATE_ROOT / "workspace.html",
        TEMPLATE_ROOT / "organization/index.html",
        TEMPLATE_ROOT / "tasks/index.html",
        TEMPLATE_ROOT / "follow-up/index.html",
        TEMPLATE_ROOT / "reports/index.html",
    )
    for page in pages:
        source = page.read_text(encoding="utf-8")
        assert "<h1" in source, page
        assert 'aria-label=' in source or "<label" in source, page


def test_dynamic_status_surfaces_are_announced():
    source = (TEMPLATE_ROOT / "tasks/index.html").read_text(encoding="utf-8")
    assert 'role="status"' in source
    assert 'caption class="sr-only"' in source


def test_roster_script_exposes_live_delivery_indicators():
    source = (STATIC_ROOT / "js/app.js").read_text(encoding="utf-8")
    assert "delivery.student_name" in source
    assert "delivery.student_nie" in source
    assert 'deliveryDate.className = "delivery-date"' in source
    assert 'evidenceCount.className = "evidence-count"' in source
    assert 'observationCount.className = "observation-count"' in source
    assert "formatDeliveryDate(payload.actual_delivered_at)" in source
    assert 'return "Sin registrar"' in source
    assert 'return "Fecha no disponible"' in source


def test_task_controls_surface_request_errors():
    source = (STATIC_ROOT / "js/app.js").read_text(encoding="utf-8")
    assert 'message.textContent = error.message;' in source
    assert 'historyButton.disabled = true;' in source
    assert 'extractErrorMessage(payload, "No se pudo cargar el historial.")' in source
    assert 'subjects/${encodeURIComponent(subjectId)}/sections/${encodeURIComponent(sectionId)}' in source


def test_report_form_surfaces_popup_blocking():
    source = (STATIC_ROOT / "js/app.js").read_text(encoding="utf-8")
    assert 'id="report-message"' in (TEMPLATE_ROOT / "reports/index.html").read_text(encoding="utf-8")
    assert 'message.textContent = reportWindow ? "El informe se abrió en una pestaña nueva."' in source


def test_form_controls_have_visible_focus_and_disabled_states():
    source = (STATIC_ROOT / "css/base.css").read_text(encoding="utf-8")
    assert "select:focus-visible" in source
    assert "textarea:focus-visible" in source
    assert "button:disabled" in source
