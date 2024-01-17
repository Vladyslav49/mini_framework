from __future__ import annotations

from http.client import responses
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mini_framework import Response


def get_status_code_and_phrase(status_code: int) -> str:
    """Get status code and phrase for a given status code."""
    if status_code not in responses:
        raise ValueError(f"Invalid status code: {status_code}")
    return f"{status_code} {responses[status_code]}"


def prepare_headers(
    response: Response,
    *,
    content: Any,
) -> list[tuple[str, str]]:
    """Prepare headers for a given response."""
    headers = [
        ("Content-Type", f"{response.media_type}; charset={response.charset}"),
        ("Content-Length", str(len(content))),
    ] + list(response.headers.items())
    return headers
