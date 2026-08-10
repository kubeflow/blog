---
toc: true
layout: post
comments: true
title: "Introducing Kubeflow MCP: An Agent Interface for Cloud Native AI at Scale"
description: "An open MCP interface that lets AI agents operate Kubeflow directly from conversation."
hide: false
categories: [release, mcp]
permalink: /introducing-kubeflow-mcp/
author: "Abhijeet Dhumal"
---

## Agent-Native Infrastructure

AI agents are rapidly becoming the primary interface for software development. Engineers use them to write code, debug systems, and automate operational workflows. But when it comes to AI infrastructure (submitting training jobs, managing GPU resources, monitoring distributed workloads) agents hit a wall. They can generate scripts and suggest commands, but they cannot interact with the cluster directly.

The **Kubeflow MCP Server** removes that wall. It exposes Kubeflow operations as [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) tools, an open standard that gives AI agents structured, discoverable access to external systems. The agent talks to Kubeflow. Kubeflow talks back.

## What This Changes

Without MCP, the workflow looks like this: you describe what you want to your agent, it generates a Python script, you run the script, something fails, you paste the error back, the agent suggests a fix, you try again. The human is the message bus between the agent and the cluster.

![From Manual Pipelines to Conversational Training](/images/2026-08-10-introducing-kubeflow-mcp/mcp-before-after.png)

With MCP, the agent calls Kubeflow tools directly. It checks your cluster, estimates resource requirements, previews the training job spec, waits for your approval, submits it, and streams logs back, all within the same conversation. You stay in control, but you're no longer the bottleneck.

Here's what a real interaction looks like:

```text
User: "Fine-tune gemma-2b on the alpaca dataset using LoRA"

1. Agent calls pre_flight(model="google/gemma-2b")
   → Trainer v2.2 installed, 4x A100 available, gemma runtime found

2. Agent calls fine_tune(model="hf://google/gemma-2b",
                         dataset="hf://tatsu-lab/alpaca",
                         runtime="torchtune-gemma-2b",
                         confirmed=False)
   → Returns full TrainJob spec for review

3. User: "Looks good, submit it"
   Agent calls fine_tune(..., confirmed=True)
   → TrainJob "train-gemma-abc" created

4. Agent calls get_training_logs("train-gemma-abc")
   → Epoch 1/3 ━━━━━━━━━━━━ 34% loss=1.42
```

Four tool calls. No YAML. No copy-pasting between tabs. The agent operated directly on the cluster, and nothing happened without the user's explicit approval.

## Where It Fits

The diagram below shows the three layers: AI agents on the left, the MCP Server in the middle translating tool calls into Kubernetes API operations, and the Kubeflow infrastructure on the right executing them.

![Kubeflow MCP Architecture](/images/2026-08-10-introducing-kubeflow-mcp/mcp-server-architecture.png)

The MCP Server is not a replacement for the [Kubeflow SDK](https://blog.kubeflow.org/sdk/intro/). It's a new interface layer that sits alongside it. The SDK is for writing Python programs. The MCP Server is for AI agents that need to *act* on your behalf.

Both are backed by the same infrastructure: Kubeflow Trainer creates TrainJobs, JobSet manages distributed execution, and Kubernetes schedules pods onto GPUs. The difference is who's driving: a Python script you wrote, or an agent you're conversing with.

The Trainer client is fully implemented today. As additional Kubeflow components gain MCP support, the same server will expose them all through a unified agent interface.

## Key Features

### Guided Workflow with 23 Tools

Tools are organized into phases that guide agents through the correct sequence:

| Phase | Tools | What they do |
|-------|-------|--------------|
| **Planning** | `pre_flight`, `check_compatibility`, `get_cluster_resources`, `estimate_resources` | Validate the cluster, estimate GPU needs, catch blockers early |
| **Discovery** | `list_training_jobs`, `get_training_job`, `list_runtimes`, `get_runtime` | Browse what's running and what runtimes are available |
| **Training** | `fine_tune`, `run_custom_training`, `run_container_training` | LoRA/QLoRA fine-tuning, custom distributed scripts, or container jobs |
| **Monitoring** | `get_training_logs`, `get_training_events`, `wait_for_training` | Stream logs, diagnose scheduling issues, wait for completion |
| **Lifecycle** | `delete_training_job`, `update_training_job` | Suspend, resume, or clean up jobs |
| **Platform** | `inspect_crd`, `inspect_controller`, `patch_runtime`, `create_runtime`, `delete_runtime` | Admin operations for CRDs and runtimes |
| **Health** | `health_check`, `get_server_logs` | Server diagnostics |

![Guided Training Workflow](/images/2026-08-10-introducing-kubeflow-mcp/mcp-workflow-phases.png)

### Two-Phase Confirmation

Every mutating operation previews first. The agent sees exactly what would happen before anything touches the cluster, and only proceeds with explicit approval. An agent can never accidentally create, delete, or modify a resource without the user seeing the full spec first.

![Two-Phase Confirmation](/images/2026-08-10-introducing-kubeflow-mcp/mcp-confirm-gate.png)

### Security

The server is designed to be safe by default:

- **Input validation**: Kubernetes names and namespaces are validated against strict patterns; injection and path traversal attempts are rejected
- **Data masking**: Tokens, passwords, and credentials are automatically masked in logs
- **DNS rebinding protection**: Host and Origin header validation on HTTP transport
- **Ownership guards**: Non-admin personas can only modify jobs created through the MCP server
- **Authentication**: Bearer token for development, JWT/JWKS verification for production

See [SECURITY.md](https://github.com/kubeflow/mcp-server/blob/main/SECURITY.md) for the full threat model and hardening guide.

### Personas

Not everyone needs the same level of access. Four built-in personas control which tools an agent can see:

| Persona | Tools available | Intended for |
|---------|----------------|--------------|
| `readonly` | 12 | Browsing, auditing, demos |
| `data-scientist` | 16 | Training and monitoring |
| `ml-engineer` | 20 | + lifecycle management |
| `platform-admin` | 23 | Full access including CRD/runtime ops |

![Persona-Based Access Control](/images/2026-08-10-introducing-kubeflow-mcp/mcp-personas.png)

```bash
kubeflow-mcp serve --persona data-scientist
```

### Token-Efficient Modes

LLMs have limited context windows. Registering all 23 tools costs ~2,400 tokens. Two alternative modes reduce this dramatically while preserving full functionality:

| Mode | Tools exposed | Token cost | How it works |
|------|---------------|------------|--------------|
| `full` | 23 | ~2,400 | All tools registered directly |
| `progressive` | 3 | ~85 | Agent discovers tools on demand via meta-tools |
| `semantic` | 2 | ~69 | Agent searches tools by natural language description |

```bash
kubeflow-mcp serve --mode progressive
```

### Platform Awareness

The server auto-detects your Kubernetes distribution and adapts its guidance:

- **OpenShift**: Adds required writable volumes, sets environment variables to avoid permission errors under restricted security contexts
- **EKS/GKE**: Detects GPU node pools and suggests tolerations
- **Kind/Minikube**: Works out of the box for local development

### Resilience

- Rate limiting protects the Kubernetes API from agent-driven burst traffic
- Circuit breaker prevents cascading failures when the cluster is unhealthy
- Structured error hints help agents diagnose and recover without human intervention

### Observability

Optional OpenTelemetry tracing covers every tool call with zero code changes:

```bash
kubeflow-mcp serve --otel-endpoint http://localhost:4318
```

Each span carries structured attributes following OpenTelemetry semantic conventions, covering tool identity, execution outcome, persona context, and session correlation for end-to-end tracing across agent sessions.

![Jaeger Trace List](/images/2026-08-10-introducing-kubeflow-mcp/jaeger-trace-list.png)

<br/>

![Jaeger Trace Waterfall](/images/2026-08-10-introducing-kubeflow-mcp/jaeger-trace-waterfall.png)

## Get Started

**Prerequisites**: Python 3.10+, a Kubernetes cluster with [Kubeflow Trainer v2.2+](https://github.com/kubeflow/trainer) installed.

```bash
pip install kubeflow-mcp
```

### Server Configuration

```bash
kubeflow-mcp serve \
  --clients trainer \             # modules: trainer, optimizer (stub), hub (stub)
  --persona ml-engineer \         # readonly | data-scientist | ml-engineer | platform-admin
  --mode full \                   # full | progressive | semantic
  --instruction-tier full \       # full | compact | minimal
  --transport stdio \             # stdio | http | sse
  --auth-token SECRET \           # bearer token for HTTP auth (dev/staging)
  --otel-endpoint URL \           # OTLP HTTP endpoint (optional tracing)
  --log-level INFO \              # DEBUG | INFO | WARNING | ERROR
  --log-format console \          # console | json (auto-detected if omitted)
  --no-banner                     # suppress startup banner
```

### Connect Your Agent

**Cursor IDE** — add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "kubeflow": {
      "command": "kubeflow-mcp",
      "args": ["serve"]
    }
  }
}
```

**Claude Code**:

```bash
claude mcp add kubeflow -- kubeflow-mcp serve
```

**HTTP (remote / team deployment)**:

```bash
kubeflow-mcp serve --transport http --auth-token $MY_TOKEN
```

Then point any MCP client at `http://your-host:8000/mcp`.

### MCP Inspector

Verify your setup using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector), a visual debugging tool that lets you browse registered tools, invoke them interactively, and inspect server responses:

```bash
make inspector
```

![MCP Inspector](/images/2026-08-10-introducing-kubeflow-mcp/mcp-inspector.png)

## What's Next?

The Trainer client ships today, but the vision is much bigger: a unified agent interface for the entire Cloud Native AI lifecycle.

| Client | Status | Description |
|--------|--------|-------------|
| **Kubeflow Trainer** | Available ✅ | Train and fine-tune AI models via MCP tools |
| **Kubeflow Optimizer (Katib)** | Planned 🚧 | Hyperparameter search, trial comparison, optimal config |
| **Model Registry** | Planned 🚧 | Model registration, promotion, lineage tracking |
| **Kubeflow Pipelines** | Planned 🚧 | Build, run, and track end-to-end ML workflows |
| **Spark Operator** | Planned 🚧 | Data processing and feature engineering |
| **Feast** | Planned 🚧 | Feature store management |

Here's what's coming beyond new clients:

- **Multi-Provider Agent Runtime**: Pluggable LLM backends (`ollama`, `litellm`) for local or cloud-routed agent inference
- **Enterprise & In-Cluster**: Native OIDC/OAuth, Kubernetes RBAC binding, Helm chart, and Agent-to-Agent (A2A) delegation
- **Advanced Training**: Checkpoint save/restore, real-time metrics, dynamic scaling, and multi-cluster support

The [ROADMAP](https://github.com/kubeflow/mcp-server/blob/main/ROADMAP.md) tracks the full phased delivery plan.

## Get Involved

The Kubeflow MCP Server is built by and for the community. We welcome contributions, feedback, and participation from everyone!

**Resources**:
- [GitHub Repo](https://github.com/kubeflow/mcp-server)
- [Documentation](https://github.com/kubeflow/mcp-server/blob/main/README.md)
- [ROADMAP](https://github.com/kubeflow/mcp-server/blob/main/ROADMAP.md)

**Connect with the Community**:
- Join [#kubeflow-ml-experience](https://cloud-native.slack.com/archives/C08KJBVDH5H) on [CNCF Slack](https://www.kubeflow.org/docs/about/community/#kubeflow-slack-channels)
- Attend the [Kubeflow SDK and ML Experience WG](https://bit.ly/kf-ml-experience) meetings
- Check out [good first issues](https://github.com/kubeflow/mcp-server/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) to get started

**Live Demo ([Open Source Summit India 2025](https://ossindia2026.sched.com/event/2KNF7/hey-ai-train-llama-making-kubeflow-agent-native-with-mcp-akash-jaiswal-oracle-abhijeet-dhumal-red-hat))**: same MCP server, three clients..

- **LangChain + LiteLLM**: pre-flight checks, confirm gate
- **Claude**: custom distributed training
- **Cursor IDE**: fine-tuning with torchtune runtime

[![Demo: Fine-tune Llama on OpenShift](https://img.youtube.com/vi/cZ2BP5hQjc8/maxresdefault.jpg)](https://youtu.be/cZ2BP5hQjc8)

---

*The Kubeflow MCP Server is an Apache 2.0 project under the [Kubeflow](https://www.kubeflow.org/) umbrella, a CNCF Sandbox project.*
