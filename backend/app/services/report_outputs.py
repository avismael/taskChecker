from typing import Protocol

from fastapi.responses import HTMLResponse, Response

from backend.app.observability.logging import log_event
from backend.app.services.report_service import csv_bytes, pdf_bytes, print_html, xlsx_bytes


class ReportOutputPort(Protocol):
    def render(self, report_type: str, rows: list[dict], format: str): ...


class DefaultReportOutput:
    def render(self, report_type: str, rows: list[dict], format: str):
        log_event("report_rendered", report_type=report_type, format=format, row_count=len(rows))
        if format == "csv":
            return Response(csv_bytes(rows), media_type="text/csv")
        if format == "xlsx":
            return Response(
                xlsx_bytes(rows),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=taskchecker-{report_type}.xlsx"},
            )
        if format == "print":
            return HTMLResponse(print_html(f"{report_type.title()} report", rows))
        if format == "pdf":
            return Response(
                pdf_bytes(f"{report_type.title()} report", rows),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=taskchecker-{report_type}.pdf"},
            )
        if format == "json":
            return {"type": report_type, "rows": rows}
        raise ValueError("Unsupported report format.")


report_output: ReportOutputPort = DefaultReportOutput()
