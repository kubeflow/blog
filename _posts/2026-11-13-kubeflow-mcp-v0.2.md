---
toc: true
layout: post
comments: true
title: "Kubeflow MCP Server v0.2: Expanding the Kubeflow Ecosystem with New Client Integrations"
description: "Kubeflow MCP Server v0.2 expands AI agent access to Kubeflow with new Pipelines, Spark, Optimizer, and Hub integrations, guided workflows, and safety-focused operations."
hide: false
categories: [release, mcp]
permalink: /kubeflow-mcp-v0.2/
author: "Pratik Naik, Abhijeet Dhumal"
---

AI agents are becoming an increasingly common interface for interacting with software systems. They can write code, debug applications, and automate development workflows. But interacting with machine learning infrastructure is a different challenge.

Kubeflow provides several components for managing the machine learning lifecycle. Training workloads, end-to-end pipelines, distributed data processing, and model management each have their own APIs, SDKs, and operational workflows.

Connecting AI agents to these capabilities requires more than exposing a collection of tools. It requires a consistent interface that allows agents to discover capabilities, execute operations, monitor workloads, and interact with infrastructure safely.

The **Kubeflow MCP Server** provides that interface through the Model Context Protocol (MCP).

With the initial v0.1 release, we introduced a Trainer-focused MCP client that enabled AI agents to interact with Kubeflow Trainer workflows directly.

With **v0.2, we are expanding that foundation into a multi-client platform.**

The new release introduces integrations for Kubeflow Pipelines, Spark, Optimizer (Katib), and Hub (Model Registry), extending agent access beyond model training into pipeline execution, Spark session management, hyperparameter optimization, and model management.

The direction is simple: one MCP server, multiple Kubeflow clients, and a unified interface for AI agents.

In this blog, we walk through what's new in v0.2, how the new client integrations work, the design principles behind them, and how to get started.

---

## What's New in v0.2?

The biggest change in v0.2 is the expansion of the client architecture.

Previously, the MCP Server primarily exposed Kubeflow Trainer functionality. The new architecture allows multiple Kubeflow components to be integrated through dedicated clients.

### Client Overview

| Client | Status | Tools | Description |
|---|---|---:|---|
| Kubeflow Trainer | Available | 23 | Training, fine-tuning, monitoring, and runtime management |
| Kubeflow Pipelines | New in v0.2 | 8 | Pipeline discovery, execution, monitoring, and lifecycle management |
| Spark | New in v0.2 | 5 | Spark session discovery, creation, monitoring, and deletion |
| Optimizer (Katib) | New in v0.2 | 8 | Hyperparameter optimization workflows |
| Hub (Model Registry) | New in v0.2 | 7 | Model registration, discovery, versions, and artifacts |

The Trainer client remains the foundation, while Pipelines, Spark, Optimizer, and Hub bring four new sets of capabilities to the MCP Server.

---

## A Unified Multi-Client Architecture

The v0.2 architecture is designed around a central MCP Server that exposes multiple Kubeflow integrations to AI agents.

Instead of requiring agents to understand and interact with different component-specific interfaces independently, they can discover and invoke capabilities through a unified MCP interface.

**Architecture:**

> **TODO:** Add updated v0.2 multi-client architecture diagram.

The architecture should illustrate:

- AI Agents and MCP clients
- Kubeflow MCP Server
- Trainer Client
- Pipelines Client
- Spark Client
- Optimizer Client
- Hub Client
- Underlying Kubeflow APIs and Kubernetes infrastructure

Each client is responsible for translating agent-facing tool calls into operations supported by its corresponding Kubeflow component.

The result is a consistent interaction model across multiple parts of the Kubeflow ecosystem.

---

## Key Features

### 1. Kubeflow Pipelines Client

One of the major additions in v0.2 is the **Kubeflow Pipelines Client**.

Kubeflow Pipelines enables users to build, execute, and manage end-to-end machine learning workflows. The new MCP integration makes these capabilities accessible to AI agents.

The Pipelines client is implemented using the Kubeflow Pipelines SDK.

**Eight tools are introduced:**

| Phase | Tools | Description |
|---|---|---|
| Discovery | `list_pipelines` | List available pipelines |
| Discovery | `get_pipeline` | Retrieve pipeline details |
| Monitoring | `list_pipeline_runs` | List pipeline runs |
| Monitoring | `get_pipeline_run` | Retrieve run details |
| Monitoring | `get_pipeline_logs` | Retrieve pipeline run logs |
| Create | `create_pipeline_run` | Create a pipeline run |
| Lifecycle | `stop_pipeline_run` | Stop a running pipeline |
| Lifecycle | `retry_pipeline_run` | Retry a pipeline run |

These tools are organized around a workflow that starts with discovering available pipelines, moves into execution and monitoring, and provides lifecycle operations when needed.

**Example interaction:**

```text
User:
"Show me the available Kubeflow pipelines."

Agent:
Calls list_pipelines()

MCP Server:
Retrieves available pipelines.

Agent:
Presents the pipeline list to the user.

User:
"Show me the details of this pipeline."

Agent:
Calls get_pipeline()
```

An agent can use these tools to discover existing workflows and interact with pipeline executions without requiring the user to manually navigate different interfaces.

> **TODO:** Add Pipelines Client demo screenshot or GIF.

**Implementation:** [Issue #182](https://github.com/kubeflow/mcp-server/issues/182) | [PR #468](https://github.com/kubeflow/mcp-server/pull/468)

---

### 2. Spark Client

The second major addition is the **Spark Client**.

Apache Spark is widely used for distributed data processing. Through the new Spark integration, AI agents can discover and manage Spark sessions using MCP tools.

The Spark client introduces five tools:

| Phase | Tool | Description |
|---|---|---|
| Discovery | `list_spark_sessions` | List available Spark sessions |
| Discovery | `get_spark_session` | Retrieve Spark session details |
| Sessions | `create_spark_session` | Create a Spark session |
| Sessions | `delete_spark_session` | Delete a Spark session |
| Monitoring | `get_spark_session_logs` | Retrieve Spark session logs |

These capabilities provide a conversational interface for Spark session management.

**Example interaction:**

```text
User:
"Show me the currently available Spark sessions."

Agent:
Calls list_spark_sessions()

MCP Server:
Retrieves Spark session information.

Agent:
Summarizes the available sessions.

User:
"Show me the logs for this session."

Agent:
Calls get_spark_session_logs()
```

The integration follows the same client-oriented approach as the other Kubeflow integrations.

> **TODO:** Add Spark Client workflow diagram or demo screenshot.

**Implementation:** [Issue #51](https://github.com/kubeflow/mcp-server/issues/51)

---

### 3. Optimizer (Katib) Client

The third addition is the **Optimizer (Katib) Client**.

Kubeflow Katib enables hyperparameter optimization for machine learning workloads. Through the new Optimizer integration, AI agents can create, monitor, and analyze hyperparameter optimization jobs using MCP tools.

The Optimizer client introduces eight tools:

| Phase | Tool | Description |
|---|---|---|
| Discovery | `list_optimization_jobs` | List optimization jobs |
| Discovery | `get_optimization_job` | Retrieve optimization job details |
| Monitoring | `get_optimization_logs` | Retrieve optimization job logs |
| Monitoring | `get_optimization_events` | Retrieve optimization job events |
| Monitoring | `wait_for_optimization` | Wait for an optimization job to complete |
| Create | `create_optimization_job` | Create a hyperparameter optimization job |
| Results | `get_best_hyperparameters` | Retrieve the best hyperparameters found |
| Lifecycle | `delete_optimization_job` | Delete an optimization job |

These capabilities provide a conversational interface for hyperparameter optimization.

**Example interaction:**

```text
User:
"Optimize the learning rate and batch size for my model."

Agent:
Calls create_optimization_job()

MCP Server:
Creates the optimization job and returns its details.

Agent:
Presents the optimization job to the user.

User:
"Which hyperparameters performed best?"

Agent:
Calls get_best_hyperparameters()
```

An agent can use these tools to launch hyperparameter searches and compare results without manually inspecting individual trials.

> **TODO:** Add Optimizer Client demo screenshot or GIF.

> **TODO:** Add implementation issue and PR links.

---

### 4. Hub (Model Registry) Client

The fourth addition is the **Hub (Model Registry) Client**.

The Model Registry enables users to register, discover, and manage machine learning models and their versions. Through the new Hub integration, AI agents can perform model management operations using MCP tools.

The Hub client introduces seven tools:

| Phase | Tool | Description |
|---|---|---|
| Discovery | `list_models` | List registered models |
| Discovery | `get_model` | Retrieve model details |
| Discovery | `list_model_versions` | List versions of a model |
| Discovery | `get_model_version` | Retrieve model version details |
| Discovery | `get_model_artifact` | Retrieve model artifact details |
| Create | `register_model` | Register a new model |
| Lifecycle | `update_model` | Update model metadata |

These capabilities provide a conversational interface for model management.

**Example interaction:**

```text
User:
"Register my newly trained model in the Model Registry."

Agent:
Calls register_model()

MCP Server:
Registers the model and returns its details.

Agent:
Confirms the registration to the user.

User:
"Show me the versions of this model."

Agent:
Calls list_model_versions()
```

The integration follows the same client-oriented approach as the other Kubeflow integrations.

> **TODO:** Add Hub Client demo screenshot or GIF.

> **TODO:** Add implementation issue and PR links.

---

### 5. Guided Tool Workflows

As the number of available tools grows, helping AI agents select the right tool becomes increasingly important.

The MCP Server organizes tools into logical workflow phases.

For example, the Trainer client follows:

1. **Planning:** Validate the environment and estimate resources.
2. **Discovery:** Find existing training jobs and available runtimes.
3. **Training:** Submit training and fine-tuning workloads.
4. **Monitoring:** Retrieve logs, events, and workload status.
5. **Lifecycle:** Manage existing training jobs.
6. **Platform:** Inspect and manage platform resources.

The Pipelines, Spark, Optimizer, and Hub clients follow similar phase-based organization.

| Client | Workflow phases |
|---|---|
| Trainer | Planning, Discovery, Training, Monitoring, Lifecycle, Platform |
| Pipelines | Discovery, Monitoring, Create, Lifecycle |
| Spark | Discovery, Sessions, Monitoring |
| Optimizer (Katib) | Discovery, Monitoring, Create, Results, Lifecycle |
| Hub (Model Registry) | Discovery, Create, Lifecycle |

This organization gives agents clearer guidance about which operations to perform and when.

**Read first. Mutate later.**

Discovery and monitoring operations provide the starting point, while operations that change infrastructure are handled separately.

> **TODO:** Add updated multi-client workflow diagram.

---

### 6. Safety-First Operations

An MCP Server that can interact with machine learning infrastructure must provide clear boundaries around what an agent can do.

The project follows a safety-focused design in which operations that modify resources require additional safeguards.

#### Two-Phase Confirmation

Mutating operations use a preview-and-confirm approach.

The agent first requests a preview with `confirmed=False`. The server returns the proposed operation for review. The operation proceeds only after explicit confirmation.

```python
# First: Preview the operation
result = await tool(
    confirmed=False
)

# Review the proposed operation.

# Second: Execute after approval
result = await tool(
    confirmed=True
)
```

Destructive operations, such as deleting resources, require particular care and are identified accordingly.

> **TODO:** Add updated confirmation workflow diagram.

#### Security and Access Boundaries

The project also incorporates security-oriented mechanisms:

- Read-only as the default persona.
- Namespace-based access policies.
- Credential redaction in logs.
- Input validation.
- Correlation IDs for request tracking.
- Explicit authorization for mutating operations.

The goal is to ensure that AI agents can interact with infrastructure while keeping users in control.

For additional details, see the project's [SECURITY.md](https://github.com/kubeflow/mcp-server/blob/main/SECURITY.md).

---

## What's Next?

The v0.2 release expands the foundation, but the broader vision is to provide AI agents with access to more of the Kubeflow ecosystem.

With Trainer, Pipelines, Spark, Optimizer, and Hub clients available, upcoming development will focus on deepening these integrations and evolving the platform around them.

### Other Areas of Development

Beyond client integrations, the project is also exploring:

- Agent-to-Agent (A2A) support.
- Agent Skills integration.
- OpenTelemetry and Prometheus-based observability.
- Improved runtime monitoring and operational metrics.

These items are roadmap directions and should not be interpreted as completed v0.2 functionality.

For the latest development status, see the [Kubeflow MCP Server ROADMAP](https://github.com/kubeflow/mcp-server/blob/main/ROADMAP.md).

---

## Get Started

The Kubeflow MCP Server is distributed as a Python package.

```bash
pip install kubeflow-mcp
```

**Prerequisites:**

- Python 3.10–3.12.
- Kubernetes cluster.
- The relevant Kubeflow components installed for the clients you intend to use.
- Appropriate Kubernetes credentials and permissions.

> **TODO:** Verify v0.2 installation requirements and supported SDK versions.

### Configure the MCP Server

The MCP Server can be configured through its CLI.

Previous releases support configuration options for client selection, persona, transport, authentication, and tool exposure modes.

> **TODO:** Add verified v0.2 multi-client configuration command.

### Connect Your AI Agent

The server is designed to work with MCP-compatible clients and AI agents.

Examples of integrations documented in the previous release include:

- Cursor IDE
- Claude Code
- Custom MCP clients

> **TODO:** Update connection examples for the v0.2 release and verify all supported configurations.

For installation and configuration details, refer to the [GitHub repository](https://github.com/kubeflow/mcp-server).

---

## Breaking Changes and Upgrade Notes

This section will document any changes that affect users upgrading from v0.1 to v0.2.

> **TODO:** Verify the final release diff and document:

1. Changes to CLI arguments and client configuration.
2. Dependency and SDK version updates.
3. Changes to tool names, arguments, and return structures.
4. Changes to authentication, personas, and authorization.
5. Migration steps for existing MCP client configurations.

Until the final release scope is confirmed, this section remains provisional.

---

## Contribute to Kubeflow MCP Server

Kubeflow MCP Server is an open-source project under the Kubeflow ecosystem.

The expansion of the MCP Server is driven by community contributions, collaboration, and feedback.

Whether you are interested in building new client integrations, improving existing tools, testing workflows, or contributing documentation, there are opportunities to get involved.

**Resources:**

- [GitHub Repository](https://github.com/kubeflow/mcp-server)
- [Documentation](https://github.com/kubeflow/mcp-server/blob/main/README.md)
- [Development Roadmap](https://github.com/kubeflow/mcp-server/blob/main/ROADMAP.md)
- [Kubeflow Community](https://www.kubeflow.org/docs/about/community/)

Join the `#kubeflow-ml-experience` channel on [CNCF Slack](https://www.kubeflow.org/docs/about/community/#kubeflow-slack-channels) to connect with contributors and participate in discussions.

We welcome feedback, ideas, and contributions from the community.

---

## References

1. [Kubeflow MCP Server GitHub Repository](https://github.com/kubeflow/mcp-server)
2. [Kubeflow MCP Server v0.2 Release Tracker – Issue #342](https://github.com/kubeflow/mcp-server/issues/342)
3. [Kubeflow Pipelines Client – PR #468](https://github.com/kubeflow/mcp-server/pull/468)
4. [Kubeflow Spark Integration – Issue #51](https://github.com/kubeflow/mcp-server/issues/51)
5. [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
6. [Kubeflow Documentation](https://www.kubeflow.org/docs/)
7. [Previous Announcement: Introducing Kubeflow MCP](https://blog.kubeflow.org/introducing-kubeflow-mcp/)

---

*The Kubeflow MCP Server is an Apache 2.0 open-source project under the Kubeflow umbrella, a CNCF Graduated project.*
