FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system taskchecker && adduser --system --ingroup taskchecker taskchecker

COPY pyproject.toml README.md ./
COPY backend ./backend
COPY frontend ./frontend

RUN pip install --no-cache-dir . \
    && mkdir -p /app/backend/storage /app/backend/.data \
    && chown -R taskchecker:taskchecker /app

USER taskchecker

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
