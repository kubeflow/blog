from __future__ import annotations

# Allow pytest to run both from this example directory and from the blog repository root.
import sys
from pathlib import Path as _ImportPath

_EXAMPLE_ROOT = _ImportPath(__file__).resolve().parents[1]
if str(_EXAMPLE_ROOT) not in sys.path:
    sys.path.insert(0, str(_EXAMPLE_ROOT))

from concurrent.futures import ThreadPoolExecutor
import sqlite3
import tempfile
from pathlib import Path

import pytest

from retry_safe_llm_eval.client import InjectedCrash, STRATEGIES, request_json, run_attempt
from retry_safe_llm_eval.service import database_connection, start_server

PROMPT = "Classify this review as positive or negative: 'The experience was excellent.'"
EXPECTED_EXECUTIONS = {
    "naive": 2,
    "saved-result": 2,
    "idempotency-key": 1,
}


@pytest.mark.parametrize("strategy", STRATEGIES)
def test_retry_after_response_before_persistence(strategy: str) -> None:
    with tempfile.TemporaryDirectory(prefix=f"test-{strategy}-") as directory:
        server, thread, base_url = start_server(Path(directory) / "state.sqlite3")
        evaluation_id = f"test-{strategy}"
        failure_token = f"fail-once-{strategy}"
        try:
            # First attempt receives the response and then fails before saving it.
            with pytest.raises(InjectedCrash, match="before persistence") as crash:
                run_attempt(base_url, evaluation_id, PROMPT, strategy, failure_token)
            first_response = crash.value.response
            assert first_response is not None

            status, stats_after_crash, _ = request_json(base_url, "/stats")
            assert status == 200
            assert stats_after_crash["evaluation_request_count"] == 1
            assert stats_after_crash["logical_execution_count"] == 1
            assert stats_after_crash["saved_result_count"] == 0
            status, missing_result, _ = request_json(base_url, f"/results/{evaluation_id}")
            assert status == 404
            assert missing_result["error"] == "result_not_found"

            # A task retry runs the worker again with the same stable identifiers.
            recovered = run_attempt(base_url, evaluation_id, PROMPT, strategy, failure_token)
            status, stats_after_retry, _ = request_json(base_url, "/stats")

            assert status == 200
            assert recovered["evaluation_id"] == evaluation_id
            assert stats_after_retry["evaluation_request_count"] == 2
            assert stats_after_retry["logical_execution_count"] == EXPECTED_EXECUTIONS[strategy]
            assert stats_after_retry["saved_result_count"] == 1

            if strategy == "idempotency-key":
                # The endpoint's durable idempotency record returns the same operation.
                assert recovered["operation_id"] == first_response["operation_id"]
                assert stats_after_retry["idempotency_record_count"] == 1
            else:
                assert recovered["operation_id"] != first_response["operation_id"]
                assert stats_after_retry["idempotency_record_count"] == 0
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


def test_saved_result_lookup_skips_endpoint_after_success() -> None:
    with tempfile.TemporaryDirectory(prefix="test-saved-result-") as directory:
        server, thread, base_url = start_server(Path(directory) / "state.sqlite3")
        try:
            first = run_attempt(base_url, "completed-eval", PROMPT, "saved-result", "")
            second = run_attempt(base_url, "completed-eval", PROMPT, "saved-result", "")
            status, stats, _ = request_json(base_url, "/stats")

            assert status == 200
            assert second == first
            assert stats["evaluation_request_count"] == 1
            assert stats["logical_execution_count"] == 1
            assert stats["saved_result_count"] == 1
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


def test_database_connection_is_closed_after_context_exit() -> None:
    """A closed DB handle lets Windows remove the temporary SQLite file."""
    with tempfile.TemporaryDirectory(prefix="test-db-close-") as directory:
        db_path = Path(directory) / "state.sqlite3"
        with database_connection(db_path) as connection:
            connection.execute("CREATE TABLE close_check (value INTEGER)")
            connection.execute("INSERT INTO close_check(value) VALUES (1)")

        with pytest.raises(sqlite3.ProgrammingError, match="closed database"):
            connection.execute("SELECT value FROM close_check")

        # Windows cannot delete a SQLite file while an unclosed connection
        # holds the file handle. Explicitly deleting it also makes that cleanup
        # requirement testable rather than relying only on temporary-directory
        # cleanup as a side effect.
        db_path.unlink()
        assert not db_path.exists()


def test_saved_result_lookup_encodes_evaluation_ids() -> None:
    """IDs containing URL-reserved characters remain a single result key."""
    with tempfile.TemporaryDirectory(prefix="test-encoded-id-") as directory:
        server, thread, base_url = start_server(Path(directory) / "state.sqlite3")
        evaluation_id = "eval / one"
        try:
            first = run_attempt(base_url, evaluation_id, PROMPT, "saved-result", "")
            second = run_attempt(base_url, evaluation_id, PROMPT, "saved-result", "")
            status, stats, _ = request_json(base_url, "/stats")

            assert status == 200
            assert second == first
            assert first["evaluation_id"] == evaluation_id
            assert stats["evaluation_request_count"] == 1
            assert stats["logical_execution_count"] == 1
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


def test_endpoint_rejects_missing_required_evaluation_fields() -> None:
    with tempfile.TemporaryDirectory(prefix="test-invalid-request-") as directory:
        server, thread, base_url = start_server(Path(directory) / "state.sqlite3")
        try:
            status, response, _ = request_json(
                base_url,
                "/evaluate",
                method="POST",
                payload={"evaluation_id": "missing-prompt"},
            )
            assert status == 400
            assert "evaluation_id and prompt are required" in response["error"]

            status, stats, _ = request_json(base_url, "/stats")
            assert status == 200
            assert stats["evaluation_request_count"] == 0
            assert stats["logical_execution_count"] == 0
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


def test_concurrent_requests_with_same_idempotency_key_execute_once() -> None:
    """SQLite serialization preserves deduplication for concurrent retries."""
    with tempfile.TemporaryDirectory(prefix="test-concurrent-idempotency-") as directory:
        server, thread, base_url = start_server(Path(directory) / "state.sqlite3")
        payload = {
            "evaluation_id": "concurrent-evaluation",
            "prompt": PROMPT,
            "idempotency_key": "concurrent-evaluation",
        }
        try:
            with ThreadPoolExecutor(max_workers=8) as executor:
                responses = list(
                    executor.map(
                        lambda _: request_json(
                            base_url, "/evaluate", method="POST", payload=payload
                        ),
                        range(8),
                    )
                )

            assert all(status == 200 for status, _, _ in responses)
            operation_ids = {body["operation_id"] for _, body, _ in responses}
            assert len(operation_ids) == 1

            status, stats, _ = request_json(base_url, "/stats")
            assert status == 200
            assert stats["evaluation_request_count"] == 8
            assert stats["logical_execution_count"] == 1
            assert stats["idempotency_record_count"] == 1
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
