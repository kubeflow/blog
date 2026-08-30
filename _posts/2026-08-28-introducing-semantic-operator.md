---
toc: true
layout: post
comments: true
title: "Introducing Semantic Operator: Governed Data Access for AI Agents"
description: "Semantic Operator gives AI agents a deterministic and governed path from certified business concepts to analytical data."
hide: false
categories: [agents, data, operators]
permalink: /introducing-semantic-operator/
author: "Vara Bonthu and Manabu McCloskey"
---

## Business decisions start with trusted data

Organizations invest significant time in business reporting. Data engineers prepare datasets. Business intelligence analysts define metrics and build reports in tools such as Power BI. Leaders use those reports to understand orders, customers, subscriptions, revenue, and operating performance.

This work is essential. A growing organization needs consistent facts to make good decisions. The report must mean the same thing to finance, sales, operations, and product teams. If a revenue calculation is wrong, a business decision based on that report can also be wrong.

Traditional reporting has a review process. Engineers and analysts inspect the data model, agree on metric definitions, validate relationships, and test the result. The dashboard is useful because people have done the work to make its numbers trustworthy.

## AI agents changed the interface

Large language models made business data accessible through natural language. Organizations are now building agents that can answer questions such as:

1. How many orders did we receive last week?
2. Which customers are at risk of leaving?
3. How many active subscribers do we have?
4. What was recurring revenue in the last quarter?

The experience is compelling. A user asks a question and receives an answer without waiting for a new dashboard.

The common implementation is also risky. The language model connects to a database, discovers tables, and writes SQL from the wording of the question. It sees schemas and column names. It often does not know the business meaning behind them.

A table called `subscriptions` does not explain which statuses count as active. A column called `revenue` does not say whether it contains gross revenue, recognized revenue, or recurring revenue. A customer table does not explain which relationship should be used when several account identifiers exist.

The model has to guess. A different phrase can lead to a different table, join, filter, or aggregation. Both SQL statements may run successfully. Both answers may look reasonable. Only one may match the definition used by the business.

![From generated SQL to certified business meaning](/images/2026-08-28-introducing-semantic-operator/problem-and-solution.svg)

This is not only a query generation problem. It is a business context problem. Returning a confident but incorrect number to a leader can affect pricing, investment, staffing, and customer decisions.

## A semantic layer provides the missing context

A [semantic layer](https://github.com/apache/ossie/blob/main/core-spec/spec.md) records the meaning that a database schema cannot express on its own. It defines datasets, fields, relationships, metrics, allowed dimensions, business descriptions, synonyms, and context for AI systems.

The agent no longer needs to invent the calculation for recurring revenue. It selects the certified revenue metric and the approved time dimension. The semantic layer owns the relationship and aggregation rules.

Different wording can still resolve to the same certified concepts. Once that happens, the same model and structured request produce the same SQL. The language model helps understand the question. Deterministic software plans the query.

This separation is critical for trustworthy analytics. The model can reason about language. It is not trusted to invent business logic.

## Semantic definitions should be portable

Many organizations started building their own semantic formats. The definition often fits one query engine, catalog, or business intelligence tool. That approach becomes difficult when a company uses several databases or lakehouse engines.

Metrics become tied to one platform. Teams repeat the same definitions for another engine. Agents receive different context depending on the data source. Moving a workload can also mean rebuilding the semantic layer.

The open source community is addressing this portability problem through [Apache Ossie](https://ossie.apache.org/). Apache Ossie defines a vendor neutral format for semantic models. It gives tools a shared way to describe datasets, fields, relationships, metrics, and AI context.

A portable specification solves one part of the problem. Organizations also need a reliable way to validate models, bind them to physical data, serve them to agents, apply governance, and create SQL for the selected query engine.

## Introducing Semantic Operator

Today we are introducing **Semantic Operator**, a [Kubernetes operator](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/) and semantic server that operationalizes Apache Ossie models.

Semantic Operator accepts an Apache Ossie based [`SemanticModel`](https://github.com/apache/ossie/blob/main/core-spec/spec.md#semantic-model) Kubernetes resource. It validates the definition and checks its physical schema bindings. It compiles a valid model into a versioned artifact. The serving layer then exposes certified concepts through [MCP](https://modelcontextprotocol.io/), REST, and governed SQL views.

When an agent asks for a metric, the language model selects from the concepts it is allowed to see. Semantic Operator applies governance and creates one deterministic SQL statement from the certified definitions. The language model does not write the SQL.

If a model update fails validation or schema checks, it is not published. The last valid version remains available. This keeps an invalid change from silently reaching every agent and application.

A notebook, dashboard, pipeline, application, and agent can now use the same business contract. The contract is portable. The query is specific to the selected engine.

Semantic Operator is now a Kubeflow subproject. The source code is available in the [Kubeflow Semantic Operator repository](https://github.com/kubeflow/semantic-operator). The [Semantic Operator documentation](https://semantic.kubeflow.org/en/latest/) includes the architecture, installation guide, model authoring guide, and runnable examples.

## Bootstrap models with ossiectl

Writing the first semantic model by hand can be slow when a platform has many tables. The [`ossiectl`](https://semantic.kubeflow.org/en/latest/architecture/ossiectl/) command helps engineers bootstrap that work from metadata they already have.

It can inspect a query engine information schema, including tables exposed through an open catalog such as [Apache Polaris](https://polaris.apache.org/). It can also enrich the result with business context from [DataHub](https://datahubproject.io/). The command writes a draft `SemanticModel` YAML file with datasets and fields. Engineers then review the draft, add certified metrics and relationships, and apply it to Kubernetes.

![How ossiectl creates a SemanticModel](/images/2026-08-28-introducing-semantic-operator/ossiectl-flow.svg)

This is an authoring step. It is not in the query path. Teams can run it when they create a model or when they want help reviewing schema changes. The generated YAML remains normal source controlled configuration that engineers can inspect and edit.

## From a semantic request to one SQL statement

An agent does not need to understand a warehouse schema or invent a join. It discovers the metrics and dimensions that it is allowed to use. It then sends a structured request through the [Model Context Protocol](https://modelcontextprotocol.io/), or MCP. Applications can use the REST interface. Business intelligence tools can use governed SQL views.

![Semantic Operator architecture](/images/2026-08-28-introducing-semantic-operator/architecture.svg)

The request follows a clear path.

1. A platform team applies an Apache Ossie model as a Kubernetes resource.
2. Semantic Operator validates the model and checks its physical bindings.
3. The operator publishes a versioned compiled model.
4. An authenticated caller selects certified metrics and dimensions.
5. Governance rules run before query planning.
6. The deterministic planner creates one SQL statement.
7. StarRocks or Trino executes the query against the existing data platform.

The same structured request, effective identity, model version, and query engine dialect produce the same SQL. This makes queries easier to review, test, and audit. Generated statements also carry the model version and a request hash for traceability.

## Governance before execution

Governance runs before query planning. Policies control which metrics and columns a role may use and can apply bounded row filters. An unauthorized request fails before SQL exists.

We are working on integrations with [Open Policy Agent](https://www.openpolicyagent.org/) and [Apache Ranger](https://ranger.apache.org/) so organizations can connect existing policy systems to semantic access decisions. These integrations are roadmap work and are not part of the initial release.

## Security by design

Semantic Operator can validate [JSON Web Tokens](https://www.rfc-editor.org/rfc/rfc7519) against an issuer's public keys. It can also run behind an authenticating proxy when trusted headers are explicitly enabled. An unverified caller receives an authentication error. A verified caller without permission receives an authorization error.

The manager and query server use separate database credentials, and the query server uses read only access. Metric expressions and row policies are validated before execution. Failed model updates do not replace the last valid model. Generated SQL includes the semantic model version and a request hash for traceability.

## Built for existing data platforms

Semantic Operator does not replace a warehouse, catalog, or processing engine. It runs on top of infrastructure that teams already operate.

[StarRocks](https://www.starrocks.io/) and [Trino](https://trino.io/) are supported today. Both use the same logical planner. Small engine interfaces handle SQL syntax, connectivity, and schema inspection. This design provides a clear path for more engines.

[Adding an engine](https://semantic.kubeflow.org/en/latest/guides/adding-an-engine/) requires two focused integrations. A dialect renders engine specific SQL. A client handles connections, queries, and schema inspection. The semantic model, governance rules, serving interfaces, and planner stay unchanged. This separation is how Trino was added alongside StarRocks. It is also the path for community support of more engines.

Model scaffolding can read information schemas through supported query engines such as StarRocks and Trino. This includes data exposed to the engine through catalogs such as Apache Polaris. DataHub can add business metadata. These integrations help teams start from their existing open source data platforms, then review and certify the result before publication.

## Why Kubeflow

Kubeflow already provides open components for training, pipelines, notebooks, model serving, model metadata, and data processing. AI systems built with those components still need trustworthy business context.

Semantic Operator adds that missing contract between AI workloads and analytical data. Pipelines can use certified metrics as inputs or evaluation outputs. Model Registry records can refer to the semantic model used for training or evaluation. Notebooks can query shared definitions instead of copying SQL. Spark jobs can prepare datasets that semantic models bind to.

The proposed [Kubeflow Agents Working Group](https://github.com/kubeflow/community/pull/1025) is a natural home for this work. MCP is a primary interface for Semantic Operator. The project will also work with the Data Working Group and Spark Operator community on data platform integrations.

Kubeflow also gives the project a vendor neutral home. Releases, security decisions, roadmaps, and ownership can develop through an open community process.

## Working with Apache Ossie

Semantic Operator implements the Apache Ossie specification. It does not own the specification.

We plan to work closely with the Apache Ossie community as the standard evolves. The project will publish a compatibility matrix for specification versions, expression dialects, and query engines. We also want Semantic Operator to become a useful Kubernetes reference implementation, with agreement from the Apache Ossie community.

Portable Ossie content will remain separate from Kubernetes specific features. This allows teams to reuse the same semantic definitions across compatible tools.

## What comes next

With the repository now in Kubeflow, the first community work will focus on a stable foundation. This includes public governance, contribution and security guidance, a release process, signed images, and a public roadmap.

Technical work will expand engine support, workload identity, multi team isolation, and storage for larger compiled models. We also plan to add Kubeflow integration examples and work toward optional inclusion in the Kubeflow Community Distribution after the project has a supported release and integration tests.

Scalability is an important part of that roadmap. We will test model compilation, schema validation, publication, and serving with large numbers of tables, models, and databases. The results will define supported limits and guide work on artifact storage, controller concurrency, and multi namespace operation.

We also plan to add [ontology support](https://github.com/apache/ossie/blob/main/ontology/ontology.md) as Apache Ossie develops that part of the specification. An ontology describes shared business concepts and how they relate across domains. The goal is to connect those concepts to semantic models without weakening deterministic planning or governance.

## Join the discussion

We welcome feedback from data engineers, platform engineers, application developers, agent builders, and business intelligence teams. We are looking for contributors who want to add query engines, dialects, catalogs, metadata tools, identity providers, policy engines, and Kubeflow integrations.

Explore the [Semantic Operator repository](https://github.com/kubeflow/semantic-operator) and follow the [documentation](https://semantic.kubeflow.org/en/latest/) for installation instructions and a runnable proof of concept. The original [subproject proposal](https://github.com/kubeflow/community/pull/1024) records the community discussion behind the move to Kubeflow. You can also learn more about the underlying standard from the [Apache Ossie project](https://ossie.apache.org/) and its [core specification](https://github.com/apache/ossie/blob/main/core-spec/spec.md).

If you have built the same metric more than once, or watched an agent produce convincing but incorrect SQL, we would like to hear from you. Bring the tools and engines that matter to your users. Help us build the integrations in the open.
