"""Worker-side request logic and deterministic failure injection."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

STRATEGIES = ("naive", "saved-result", "idempotency-key")


class InjectedCrash(RuntimeError):
    """Simulates a worker losing its process after a response, before saving it."""

    def __init__(self, message: str, response: dict[str, Any] | None = None):
        super().__init__(message)
        self.response = response


def request_json(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any], dict[str, str]]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        f"{base_url.rstrip('/')}{path}",
        data=body,
        method=method,
        headers={"Content-Type": "application/json"} if body is not None else {},
    )
    try:
        with urlopen(request, timeout=5) as response:
            content = response.read().decode("utf-8")
            return (
                response.status,
                json.loads(content) if content else {},
                {key.lower(): value for key, value in response.headers.items()},
            )
    except HTTPError as error:
        content = error.read().decode("utf-8")
        try:
            data = json.loads(content) if content else {}
        except json.JSONDecodeError:
            data = {"error": content}
        return error.code, data, {key.lower(): value for key, value in error.headers.items()}
    except URLError as error:
        raise RuntimeError(f"Could not reach mock endpoint at {base_url}: {error}") from error


def run_attempt(
    base_url: str,
    evaluation_id: str,
    prompt: str,
    strategy: str,
    failure_token: str,
) -> dict[str, Any]:
    """Run one worker attempt. A crash occurs after response receipt, before save."""
    if strategy not in STRATEGIES:
        raise ValueError(f"Unknown strategy {strategy!r}; choose from {STRATEGIES}")

    if strategy != "naive":
        status, saved, _ = request_json(base_url, f"/results/{quote(evaluation_id, safe='')}")
        if status == 200:
            return saved
        if status != 404:
            raise RuntimeError(f"Result lookup failed ({status}): {saved}")

    payload: dict[str, Any] = {
        "evaluation_id": evaluation_id,
        "prompt": prompt,
        "failure_token": failure_token,
    }
    if strategy == "idempotency-key":
        payload["idempotency_key"] = evaluation_id

    status, response, headers = request_json(base_url, "/evaluate", method="POST", payload=payload)
    if status != 200:
        raise RuntimeError(f"Mock LLM request failed ({status}): {response}")

    # Deliberately fail before POST /results. The endpoint response is already
    # received, but the worker's persistent result store still has no record.
    if headers.get("x-injected-crash", "").lower() == "true":
        raise InjectedCrash(
            f"Injected crash after response for {evaluation_id}, before persistence",
            response=response,
        )

    status, saved, _ = request_json(
        base_url,
        "/results",
        method="POST",
        payload={"evaluation_id": evaluation_id, "response": response},
    )
    if status != 200 or not saved.get("saved"):
        raise RuntimeError(f"Could not persist result ({status}): {saved}")
    return response
