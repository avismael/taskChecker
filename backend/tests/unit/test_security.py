from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile
from starlette.requests import Request

from backend.app.api.security import enforce_rate_limit, read_upload


def test_rate_limit_rejects_after_limit():
    request = Request({"type": "http", "client": ("security-test", 1234)})
    enforce_rate_limit(request, "test", 1)
    with pytest.raises(HTTPException) as error:
        enforce_rate_limit(request, "test", 1)
    assert error.value.status_code == 429


def test_rate_limit_uses_separate_keys():
    request = Request({"type": "http", "client": ("security-test-keys", 1234)})
    enforce_rate_limit(request, "one", 1)
    enforce_rate_limit(request, "two", 1)


@pytest.mark.anyio
async def test_upload_limit_rejects_oversized_content():
    upload = UploadFile(file=BytesIO(b"12345"), filename="file.txt")
    with pytest.raises(HTTPException) as error:
        await read_upload(upload, 4)
    assert error.value.status_code == 413
