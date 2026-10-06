import pytest

from backend.app.services.report_outputs import report_output


def test_report_output_port_renders_pdf():
    response = report_output.render("pending", [], "pdf")
    assert response.media_type == "application/pdf"
    assert response.body.startswith(b"%PDF")


def test_report_output_port_renders_print_and_rejects_unknown_format():
    response = report_output.render("individual", [{"student": "Ana"}], "print")
    assert response.media_type == "text/html"
    assert "Ana" in response.body.decode()

    with pytest.raises(ValueError, match="Unsupported report format"):
        report_output.render("individual", [], "docx")
