#!/usr/bin/env python3
"""Run all retry scenarios locally without Kubernetes or a real LLM API."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from retry_safe_llm_eval.client import InjectedCrash, STRATEGIES, run_attempt, request_json
from retry_safe_llm_eval.service import start_server

PROMPT = "Classify this review as positive or negative: 'The experience was excellent.'"


def run_scenario(strategy: str) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix=f"retry-lab-{strategy}-") as directory:
        db_path = Path(directory) / "state.sqlite3"
        server, thread, base_url = start_server(db_path)
        try:
            evaluation_id = f"demo-{strategy}"
            failure_token = f"crash-once-{strategy}"
            attempts = 0
            for attempts in range(1, 3):
                try:
                    result = run_attempt(
                        base_url, evaluation_id, PROMPT, strategy, failure_token
                    )
                    break
                except InjectedCrash:
                    if attempts == 2:
                        raise
            else:  # pragma: no cover - defensive guard
                raise RuntimeError("The retry loop ended without a result")

            status, stats, _ = request_json(base_url, "/stats")
            if status != 200:
                raise RuntimeError(f"Could not read statistics: {stats}")
            return {
                "strategy": strategy,
                "attempts": attempts,
                "operation_id": result["operation_id"],
                **stats,
            }
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


def main() -> None:
    results = [run_scenario(strategy) for strategy in STRATEGIES]
    print(json.dumps(results, indent=2, sort_keys=True))

    by_strategy = {item["strategy"]: item for item in results}
    assert by_strategy["naive"]["logical_execution_count"] == 2
    assert by_strategy["saved-result"]["logical_execution_count"] == 2
    assert by_strategy["idempotency-key"]["logical_execution_count"] == 1
    assert all(item["evaluation_request_count"] == 2 for item in results)
    assert all(item["saved_result_count"] == 1 for item in results)
    print("\nPASS: expected duplicate-execution and recovery behavior observed.")


if __name__ == "__main__":
    main()
