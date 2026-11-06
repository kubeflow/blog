"""A small HTTP mock endpoint with durable, endpoint-side idempotency.

This uses only the Python standard library. The endpoint writes an idempotency
record before returning a response, so a retry with the same key can retrieve
that response without repeating the mocked model execution.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import unquote, urlparse


@contextmanager
def database_connection(db_path: str | Path) -> Iterator[sqlite3.Connection]:
    """Yield a transaction-scoped SQLite connection and always close it.

    The sqlite3 connection context manager commits or rolls back, but does not
    close the connection. Explicit closure is important on Windows, where an
    open SQLite handle prevents TemporaryDirectory from deleting the database.
    """
    connection = sqlite3.connect(db_path, timeout=10)
    try:
        with connection:
            yield connection
    finally:
        connection.close()


class LabHTTPServer(ThreadingHTTPServer):
    # Wait for request handlers to finish before server_close returns. This
    # prevents database handles from outliving the test's temporary directory.
    daemon_threads = False
    block_on_close = True
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], db_path: str | Path):
        self.db_path = str(db_path)
        super().__init__(address, LabRequestHandler)
        initialize_database(self.db_path)


def initialize_database(db_path: str | Path) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with database_connection(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS counters (
                name TEXT PRIMARY KEY,
                value INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS idempotency_records (
                idempotency_key TEXT PRIMARY KEY,
                evaluation_id TEXT NOT NULL,
                response_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS injected_failures (
                failure_token TEXT PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS evaluation_results (
                evaluation_id TEXT PRIMARY KEY,
                response_json TEXT NOT NULL
            );
            INSERT OR IGNORE INTO counters(name, value) VALUES ('requests', 0);
            INSERT OR IGNORE INTO counters(name, value) VALUES ('executions', 0);
            """
        )


class LabRequestHandler(BaseHTTPRequestHandler):
    server: LabHTTPServer

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        # Keep deterministic test output readable; errors are returned as JSON.
        return

    def _send_json(self, status: int, value: dict[str, Any], *, injected: bool = False) -> None:
        body = json.dumps(value, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if injected:
            self.send_header("X-Injected-Crash", "true")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0:
                return {}
            value = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(value, dict):
                raise ValueError("Expected a JSON object")
            return value
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as error:
            raise ValueError(f"Invalid JSON request: {error}") from error

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        if parsed.path == "/stats":
            with database_connection(self.server.db_path) as connection:
                counters = dict(connection.execute("SELECT name, value FROM counters"))
                idempotency_records = connection.execute(
                    "SELECT COUNT(*) FROM idempotency_records"
                ).fetchone()[0]
                saved_results = connection.execute(
                    "SELECT COUNT(*) FROM evaluation_results"
                ).fetchone()[0]
            self._send_json(
                200,
                {
                    "evaluation_request_count": counters.get("requests", 0),
                    "logical_execution_count": counters.get("executions", 0),
                    "idempotency_record_count": idempotency_records,
                    "saved_result_count": saved_results,
                },
            )
            return
        if parsed.path.startswith("/results/"):
            evaluation_id = unquote(parsed.path.removeprefix("/results/"))
            with database_connection(self.server.db_path) as connection:
                row = connection.execute(
                    "SELECT response_json FROM evaluation_results WHERE evaluation_id = ?",
                    (evaluation_id,),
                ).fetchone()
            if row is None:
                self._send_json(404, {"error": "result_not_found"})
            else:
                self._send_json(200, json.loads(row[0]))
            return
        self._send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        try:
            payload = self._read_json()
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
            return

        if parsed.path == "/evaluate":
            self._evaluate(payload)
            return
        if parsed.path == "/results":
            evaluation_id = str(payload.get("evaluation_id", ""))
            response = payload.get("response")
            if not evaluation_id or not isinstance(response, dict):
                self._send_json(400, {"error": "evaluation_id and response object are required"})
                return
            with database_connection(self.server.db_path) as connection:
                connection.execute(
                    "INSERT INTO evaluation_results(evaluation_id, response_json) VALUES (?, ?) "
                    "ON CONFLICT(evaluation_id) DO UPDATE SET response_json = excluded.response_json",
                    (evaluation_id, json.dumps(response, sort_keys=True)),
                )
            self._send_json(200, {"saved": True, "evaluation_id": evaluation_id})
            return
        if parsed.path == "/reset":
            with database_connection(self.server.db_path) as connection:
                connection.execute("DELETE FROM idempotency_records")
                connection.execute("DELETE FROM injected_failures")
                connection.execute("DELETE FROM evaluation_results")
                connection.execute("UPDATE counters SET value = 0")
            self._send_json(200, {"reset": True})
            return
        self._send_json(404, {"error": "not_found"})

    def _evaluate(self, payload: dict[str, Any]) -> None:
        evaluation_id = str(payload.get("evaluation_id", ""))
        prompt = str(payload.get("prompt", ""))
        idempotency_key_value = payload.get("idempotency_key")
        idempotency_key = str(idempotency_key_value) if idempotency_key_value else None
        failure_token_value = payload.get("failure_token")
        failure_token = str(failure_token_value) if failure_token_value else None
        if not evaluation_id or not prompt:
            self._send_json(400, {"error": "evaluation_id and prompt are required"})
            return

        # A single SQLite transaction makes the mock's idempotency record durable
        # before the HTTP response is sent. This is the guarantee being modeled.
        with database_connection(self.server.db_path) as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("UPDATE counters SET value = value + 1 WHERE name = 'requests'")
            row = None
            if idempotency_key:
                row = connection.execute(
                    "SELECT response_json FROM idempotency_records WHERE idempotency_key = ?",
                    (idempotency_key,),
                ).fetchone()

            if row is not None:
                response = json.loads(row[0])
            else:
                response = {
                    "evaluation_id": evaluation_id,
                    "operation_id": str(uuid.uuid4()),
                    "label": "positive",
                    "score": 0.91,
                    "model": "mock-llm",
                }
                connection.execute("UPDATE counters SET value = value + 1 WHERE name = 'executions'")
                if idempotency_key:
                    connection.execute(
                        "INSERT INTO idempotency_records(idempotency_key, evaluation_id, response_json) "
                        "VALUES (?, ?, ?)",
                        (idempotency_key, evaluation_id, json.dumps(response, sort_keys=True)),
                    )

            inject_crash = False
            if failure_token:
                cursor = connection.execute(
                    "INSERT OR IGNORE INTO injected_failures(failure_token) VALUES (?)",
                    (failure_token,),
                )
                inject_crash = cursor.rowcount == 1
            connection.commit()

        self._send_json(200, response, injected=inject_crash)


def start_server(db_path: str | Path, host: str = "127.0.0.1", port: int = 0):
    """Start a local server in a daemon thread; returns server, thread, base URL."""
    server = LabHTTPServer((host, port), db_path)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://{host}:{server.server_address[1]}"
