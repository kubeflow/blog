---
title: "Retry-Safe LLM Evaluation Jobs in Kubeflow Pipelines"
layout: post
toc: true
comments: true
image: images/logo.png
categories: [kfp, llmops]
author: "Tiru Venkatesh"
---

An LLM evaluation task can fail even after the model endpoint has returned a response. If the worker crashes before saving that response, Kubeflow Pipelines may retry the task. The next attempt can call the endpoint again, potentially repeating work or cost.

The tricky part is the gap between two separate events: the external operation completed, but the workflow's durable result record did not. A lookup in the result store cannot find a result that was never saved.

This walkthrough reproduces that failure window with a mocked LLM endpoint and compares three approaches: naive retries, persistent-result lookup, and endpoint-side idempotency keys. The companion lab is in [`examples/retry-safe-llm-eval/`](https://github.com/kubeflow/blog/tree/master/examples/retry-safe-llm-eval). It runs locally without Kubernetes or a real LLM API, and includes a Kubeflow Pipelines v2 pipeline definition for running the same scenarios in a KFP environment.

## What we want to learn

The lab asks one narrow question: after a response has arrived but before the worker persists the result, what does a task retry do?

We deliberately keep the model endpoint mocked. The example is intended to make failure and recovery behavior reproducible, not to benchmark model quality, latency, token usage, or provider billing. We also record requests to the evaluation endpoint separately from logical mock executions. A repeated HTTP request does not always imply a repeated underlying operation; that distinction is central to evaluating deduplication.

## The failure window

A typical task follows this sequence:

1. The worker sends an evaluation request with a stable evaluation ID.
2. The endpoint processes the request and returns a response.
3. The worker fails before persisting the result in the evaluation-result store.
4. Kubeflow Pipelines retries the task, which starts the worker code again.
5. The new attempt checks the result store and may submit another endpoint request.

<img src="/images/2026-10-20-retry-safe-llm-eval/retry-failure-window.svg" alt="The response-before-persistence failure window and a comparison of naive retries, saved-result lookup, and endpoint-side idempotency." width="100%">

The diagram shows why a persistent result lookup helps only when a completed result is already present. The retry cannot recover the first response from a result store that has no record of it.

## Three strategies

### 1. Naive retries

The worker calls the endpoint and attempts to save its response. If it fails before persistence, the retry simply calls the endpoint again. This is the baseline we want to compare against.

### 2. Persistent-result lookup

Before making an endpoint request, the worker looks for a saved result associated with the evaluation ID. If a result exists, it returns it and avoids the endpoint call. If no result exists, it calls the endpoint and attempts to save the response.

This check is useful after a successful save: rerunning the same completed evaluation can reuse its result. But it does not close the response-before-persistence window. In the injected failure, the lookup correctly returns “not found,” because there is no result to retrieve. The retry must still call the endpoint.

### 3. Endpoint-side idempotency key

The worker sends a stable idempotency key—here, the evaluation ID—with the request. The mock endpoint stores the generated response against that key before returning it. When the same key arrives again, the endpoint returns the stored response instead of executing the mock operation a second time.

This strategy has an additional requirement: the endpoint, or the upstream provider, must durably deduplicate requests by key. A client-side key alone does nothing. A wrapper that calls an external LLM and crashes before it saves the external response may still issue that external call again unless the provider supplies compatible idempotency semantics or a durable reconciliation mechanism.

## Run the reproduction

You need Python 3.10 or newer. The local demo uses the Python standard library; `pytest` is needed only for the automated tests. No Kubernetes cluster, cloud credentials, or model API key is required.

Clone or download the companion source, then enter the lab directory:

```bash
cd examples/retry-safe-llm-eval
python run_demo.py
```

The demo starts a local HTTP server backed by a temporary SQLite database. A one-shot failure marker makes the worker raise an error after it has received the endpoint response but before it posts that response to the result store. The same failure token is reused on the retry, so the fault occurs only once. This deterministic injection represents the recovery boundary without relying on timing or killing a process at an unpredictable point.

The lab assertions check the recovery outcome and the count of logical executions. You can run the tests separately:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

The tests also check that the result store is empty immediately after the injected failure and that saved-result lookup skips the endpoint when a result has already been persisted.

## Observed behavior in the mock

With one injected failure and one retry, the local demo produced these counts:

| Strategy | Evaluation endpoint requests | Mock logical executions | Saved results after recovery |
| --- | ---: | ---: | ---: |
| Naive retry | 2 | 2 | 1 |
| Persistent-result lookup | 2 | 2 | 1 |
| Endpoint idempotency key | 2 | 1 | 1 |

These are results from the local mock and its automated tests, not measurements from a real LLM provider. All three strategies make two `POST /evaluate` requests because the first response has already returned before the worker fails. These counts do not include result lookups, result writes, or statistics requests. The difference is whether the second request causes another mock execution. In the idempotency-key case, the endpoint recognizes the key and returns its previously stored response.

## Where Kubeflow Pipelines fits

Kubeflow Pipelines lets a pipeline author configure retries on a task. The lab's `pipeline.py` defines one task for each strategy and sets one retry with `set_retry(num_retries=1, backoff_duration="0s")`. Each attempt receives the same evaluation ID and failure token. The endpoint and its state store live outside the retried task so the retry can consult durable state.

Compile the KFP v2 pipeline definition with the SDK:

```bash
python -m pip install -r requirements-kfp.txt
python pipeline.py
```

This produces `retry-safe-llm-evaluation.yaml`; compilation alone does not execute the pipeline. The side-effecting tasks have caching disabled so a previous successful task output cannot bypass the requests this experiment is intended to observe. To run it, build and deploy the mock endpoint using the included Dockerfile and Kubernetes manifest, make sure the endpoint has persistent storage, and submit the compiled pipeline to a KFP v2 installation. The lab README documents the build, deployment, and endpoint URL steps. Use a new experiment ID for each run to avoid reusing old result or idempotency records.

A key design point is that the mock's database is not stored in the retried worker pod. If it were, the state could disappear with the failed attempt, making the example unreliable and hiding the behavior we want to observe. The sample deploys one service replica with a persistent volume for its SQLite database; it is intended for a lab, not horizontal production use.

## What the experiment does—and does not—guarantee

The experiment demonstrates three narrow points:

- A task retry can repeat an external request when the response was received but the result was not persisted.
- Looking up the workflow's saved result avoids repeat requests only after a result has been saved.
- Server-side idempotency can prevent repeated logical execution when the endpoint reliably stores and returns the prior result for a stable key.

It does not prove exactly-once execution for arbitrary HTTP services or real model providers. The mock commits its idempotency record before sending the first response. A real service must provide a comparable guarantee, or the remaining failure window must be addressed through provider-side idempotency, a durable request ledger, reconciliation, or application-specific recovery logic. If the endpoint calls a separate LLM provider, its own record cannot retroactively make that provider call atomic.

The lab also does not treat [Kubeflow Pipelines caching](https://www.kubeflow.org/docs/components/pipelines/user-guides/core-functions/caching/) as a replacement for idempotency. Caching concerns reuse of completed task outputs; it does not by itself make an external side effect safe when a task fails before its output is recorded. The pipeline disables caching for these tasks so that a previous successful task output cannot hide the effect under study.

## Takeaways

Retry configuration and side-effect safety are different concerns. Retries help recover from task failures, but they can repeat operations outside the pipeline's result store. Persistent-result lookup is still valuable, but it cannot find a response that was never saved. For external APIs, robust retry behavior depends on stable identifiers and an explicit idempotency or reconciliation contract at the system that owns the side effect.

The companion lab provides a small reproduction that readers can run, inspect, and modify before adapting the pattern to their own evaluation workloads. The next step for a real deployment is to verify the idempotency contract of the provider being called and to test its failure boundaries—not to assume that a stable key alone guarantees exactly-once execution.

## References

- [Kubeflow Pipelines user guides](https://www.kubeflow.org/docs/components/pipelines/user-guides/)
- [Kubeflow Pipelines caching](https://www.kubeflow.org/docs/components/pipelines/user-guides/core-functions/caching/)
- [Kubeflow Pipelines v2 SDK on PyPI](https://pypi.org/project/kfp/)
- [Original Kubeflow community blog proposal](https://github.com/kubeflow/community/issues/1038)
