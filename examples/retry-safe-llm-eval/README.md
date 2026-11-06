# Retry-safe LLM evaluation jobs in Kubeflow Pipelines

This lab reproduces one specific failure window: the worker receives a response
from a mocked LLM endpoint, then fails before persisting that response as the
completed evaluation result. A task retry runs the evaluation logic again.

It compares three strategies:

1. **Naive retry** — call the endpoint again without checking saved results.
2. **Saved-result lookup** — check persistent evaluation-result storage before
   calling the endpoint. This avoids calls after a result has been saved, but
   does not close the response-before-persistence window.
3. **Endpoint idempotency key** — use a stable evaluation ID as an idempotency
   key. The mock endpoint durably records its response with that key before
   returning, so the retry gets the previous response without repeating the
   mocked logical execution.

The endpoint is deliberately a mock. It does not call an external model or incur
LLM API charges.

## Requirements

- Python 3.10 or newer for the local demo; the server container uses Python 3.11.
- `pytest` only if you want to run the test suite.
- Optional: Kubeflow Pipelines SDK 2.17.0 to compile the pipeline definition.
- Optional: a Kubernetes/Kubeflow Pipelines environment to run the compiled
  pipeline. A deployed endpoint with persistent storage must be reachable from
  the task pods.

## 1. Run the local demo

From this directory:

```bash
python run_demo.py
```

The demo starts an HTTP server with a temporary SQLite database, runs each
strategy with one injected failure and one retry, prints request/execution
counts, and asserts the expected behavior. It needs no Kubernetes cluster or
external API key.

## 2. Run the tests

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

The tests verify the response-before-persistence failure window, endpoint request and logical execution counts, URL-encoded evaluation IDs, invalid request handling, concurrent requests sharing an idempotency key, Windows-safe SQLite cleanup, and saved-result lookup after a successful persistence.

## 3. Compile the Kubeflow Pipelines v2 pipeline

```bash
python -m pip install -r requirements-kfp.txt
python pipeline.py
```

This writes `retry-safe-llm-evaluation.yaml`. The pipeline has one task per
strategy, disables task caching for this side-effect experiment, and sets
`num_retries=1`. The first worker attempt receives the injected-crash response
and exits unsuccessfully; KFP retries the task, which uses the same evaluation
ID and failure token.

Compilation does not execute the pipeline. To execute it, deploy the mock
service and submit the compiled YAML to a KFP v2 installation.

## 4. Deploy the mock endpoint for KFP task pods

Build and push the container image to a registry accessible by your cluster:

```bash
docker build -t ghcr.io/YOUR-OWNER/retry-safe-llm-eval:0.1.0 .
docker push ghcr.io/YOUR-OWNER/retry-safe-llm-eval:0.1.0
```

Edit `k8s/mock-endpoint.yaml` to replace the image placeholder, then apply it in
the namespace where you want the service to run:

```bash
kubectl apply -f k8s/mock-endpoint.yaml
kubectl rollout status deployment/retry-safe-llm-eval
kubectl get service retry-safe-llm-eval
```

Pass a URL reachable from KFP task pods as `base_url`. If the service is in the
`default` namespace, its in-cluster DNS name is usually
`http://retry-safe-llm-eval.default.svc.cluster.local:8080`; use the actual
namespace and cluster DNS configuration for your environment. If you use a
pipeline UI or client, set `experiment_id` to a new value for each run so that
old saved results and idempotency records do not collide with a new experiment.

This lab's SQLite database is stored on a PVC and the mock runs as a single
replica. Do not scale this SQLite deployment horizontally. A production service
would typically use an appropriate shared database and provider-supported
idempotency semantics.

## 5. Run a persistent local endpoint or reset its state (optional)

For manual inspection, start the endpoint in a separate terminal. It stores state
in the file you provide, so restarting the process reuses the same results:

```bash
python -m retry_safe_llm_eval.server --host 127.0.0.1 --port 8080 --db-path ./state.sqlite3
```

Keep this mock endpoint on a trusted local network; it has no authentication and
is intended only for a controlled lab. The Kubernetes manifest uses an internal
`ClusterIP` service rather than publishing it publicly.

To clear the state of a running local service, POST an empty JSON object to
`/reset`. Example:

```bash
python - <<'PY'
import json
from urllib.request import Request, urlopen
request = Request('http://127.0.0.1:8080/reset', data=b'{}', method='POST',
                  headers={'Content-Type': 'application/json'})
with urlopen(request) as response:
    print(response.read().decode())
PY
```

The endpoint also exposes `/health`, `/stats`, and `GET /results/{evaluation_id}`
for diagnosis.

## Expected local result

The precise operation UUIDs vary, but the counts should be:

| Strategy | Endpoint evaluation requests | Mock logical executions | Saved results |
|---|---:|---:|---:|
| Naive retry | 2 | 2 | 1 |
| Saved-result lookup | 2 | 2 | 1 |
| Idempotency key | 2 | 1 | 1 |

The `evaluation_request_count` field counts only calls to `POST /evaluate`; it does not count health checks, statistics reads, result lookups, or result writes. A repeated evaluation request is not necessarily a repeated logical execution. The mock records those counts separately to make this distinction explicit.

## Failure/recovery sequence

```mermaid
sequenceDiagram
    participant K as KFP worker
    participant E as Mock LLM endpoint
    participant R as Persistent result store
    K->>E: Evaluate (stable evaluation ID)
    E-->>K: Response; one-shot crash marker
    Note over K: Worker fails before saving result
    Note over R: No completed evaluation result exists
    K->>E: KFP retries task; same evaluation ID
    alt Naive or saved-result lookup
        E->>E: Execute mock operation again
        E-->>K: New response
    else Idempotency-key deduplication
        E->>E: Find previously stored idempotency response
        E-->>K: Original response
    end
    K->>R: Persist result
```

## Guarantees and limitations

- Saved-result lookup is useful for avoiding repeated work after successful
  persistence. It is not sufficient when the worker fails before persistence.
- The idempotency-key case only avoids a second mocked logical execution because
  this endpoint stores the response and key before sending the first response.
  A real API must provide compatible server-side idempotency semantics for this
  behavior to carry over.
- If the endpoint performs an external LLM call and crashes after that call but
  before recording the idempotency key/result, it may still repeat the external
  call unless the upstream provider also offers idempotency or another durable
  reconciliation mechanism.
- The result store and idempotency table are separate on purpose. The exercise
  demonstrates that the worker's saved-result table can be empty even though an
  idempotent endpoint already has the response.
- KFP retries re-run failed component tasks. This lab does not claim global
  exactly-once semantics for external side effects.
- The mock returns a deterministic label and score; it does not measure LLM
  quality, latency, tokens, or provider billing.
