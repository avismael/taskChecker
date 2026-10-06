from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request, UploadFile
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

_attempts: dict[str, deque[float]] = defaultdict(deque)
_attempts_lock = Lock()


def reset_rate_limits() -> None:
    with _attempts_lock:
        _attempts.clear()


def enforce_rate_limit(request: Request, key: str, limit: int, window_seconds: int = 60) -> None:
    now = monotonic()
    with _attempts_lock:
        attempts = _attempts[f"{request.client.host if request.client else 'unknown'}:{key}"]
        while attempts and now - attempts[0] >= window_seconds:
            attempts.popleft()
        if len(attempts) >= limit:
            raise HTTPException(status_code=429, detail="Too many requests. Try again later.")
        attempts.append(now)


async def read_upload(upload: UploadFile, max_bytes: int) -> bytes:
    content = await upload.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail="Uploaded file is too large.")
    return content


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        browser_request = request.headers.get("sec-fetch-site") in {"same-origin", "same-site"}
        protected_method = request.method in {"POST", "PUT", "PATCH", "DELETE"}
        exempt_path = request.url.path in {"/auth/login", "/auth/register", "/auth/recovery"}
        if browser_request and protected_method and not exempt_path and request.session.get("account_id"):
            expected = request.session.get("csrf_token")
            supplied = request.headers.get("X-CSRF-Token")
            if not expected or supplied != expected:
                return JSONResponse(status_code=403, content={"detail": "CSRF validation failed."})
        return await call_next(request)
