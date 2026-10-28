"""Kubeflow Pipelines v2 definition for the retry-safety lab.

The mock service must be reachable from KFP task pods at ``base_url`` and must
use durable storage. See README.md for the local demo and deployment notes.
"""

from kfp import compiler, dsl


@dsl.component(base_image="python:3.11-slim")
def evaluate_once(
    base_url: str,
    experiment_id: str,
    prompt: str,
    strategy: str,
) -> str:
    """Perform one attempt; KFP task retry will re-run this whole component."""
    import json
    from urllib.error import HTTPError, URLError
    from urllib.parse import quote
    from urllib.request import Request, urlopen

    def call(path: str, method: str = "GET", body: dict | None = None):
        data = None if body is None else json.dumps(body).encode("utf-8")
        request = Request(
            f"{base_url.rstrip('/')}{path}",
            data=data,
            method=method,
            headers={"Content-Type": "application/json"} if data is not None else {},
        )
        try:
            with urlopen(request, timeout=10) as response:
                return response.status, json.loads(response.read().decode("utf-8")), dict(response.headers)
        except HTTPError as error:
            content = error.read().decode("utf-8")
            return error.code, json.loads(content) if content else {}, dict(error.headers)
        except URLError as error:
            raise RuntimeError(f"Mock endpoint is unreachable: {error}") from error

    if strategy not in ("naive", "saved-result", "idempotency-key"):
        raise ValueError(f"Unsupported strategy: {strategy}")
    # Derive stable identifiers inside the component rather than combining
    # pipeline parameters with a container-only command-line placeholder.
    evaluation_id = f"{experiment_id}-{strategy}"
    failure_token = f"{experiment_id}-crash-once-{strategy}"

    if strategy != "naive":
        status, saved, _ = call(f"/results/{quote(evaluation_id, safe='')}")
        if status == 200:
            return json.dumps(saved, sort_keys=True)
        if status != 404:
            raise RuntimeError(f"Result lookup failed: HTTP {status}: {saved}")

    payload = {
        "evaluation_id": evaluation_id,
        "prompt": prompt,
        "failure_token": failure_token,
    }
    if strategy == "idempotency-key":
        payload["idempotency_key"] = evaluation_id

    status, result, headers = call("/evaluate", method="POST", body=payload)
    if status != 200:
        raise RuntimeError(f"Mock LLM call failed: HTTP {status}: {result}")
    if headers.get("X-Injected-Crash", headers.get("x-injected-crash", "")).lower() == "true":
        raise RuntimeError("Injected crash after response, before result persistence")

    status, saved, _ = call(
        "/results",
        method="POST",
        body={"evaluation_id": evaluation_id, "response": result},
    )
    if status != 200 or not saved.get("saved"):
        raise RuntimeError(f"Result persistence failed: HTTP {status}: {saved}")
    return json.dumps(result, sort_keys=True)


@dsl.pipeline(
    name="retry-safe-llm-evaluation",
    description="Compare retry behavior for a mocked LLM evaluation endpoint.",
)
def retry_safe_llm_evaluation(
    base_url: str,
    experiment_id: str,
    prompt: str = "Classify this review as positive or negative: 'The experience was excellent.'",
):
    """Run the three strategies with one retry each."""
    strategies = ("naive", "saved-result", "idempotency-key")
    for strategy in strategies:
        task = evaluate_once(
            base_url=base_url,
            experiment_id=experiment_id,
            prompt=prompt,
            strategy=strategy,
        )
        task.set_display_name(strategy)
        # This lab compares external side effects; do not let prior successful
        # task outputs bypass a new experiment's endpoint requests.
        task.set_caching_options(enable_caching=False)
        task.set_retry(num_retries=1, backoff_duration="0s")


if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=retry_safe_llm_evaluation,
        package_path="retry-safe-llm-evaluation.yaml",
    )
    print("Compiled retry-safe-llm-evaluation.yaml")
