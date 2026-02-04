---
toc: true
layout: post
comments: true
title: "Introducing Metaflow-Kubeflow Integration"
hide: false
categories: [community]
permalink: /metaflow/
---

# A tale of two flows: Metaflow and Kubeflow

Metaflow is a Python framework for building and operating ML and AI projects, originally developed and open-sourced by Netflix in 2019\. In many ways, Kubeflow and Metaflow are cousins: closely related in spirit, but designed with distinct goals and priorities.

[Metaflow](https://docs.metaflow.org/) emerged from Netflix’s need to empower data scientists and ML/AI developers with developer-friendly, Python-native tooling, so that they could easily iterate quickly on ideas, compare modeling approaches, and ship the best solutions to production without heavy engineering or DevOps involvement. On the infrastructure side, Metaflow started with AWS-native services like AWS Batch and Step Functions, later expanding to provide first-class support for the Kubernetes ecosystem and other hyperscaler clouds.

In contrast, Kubeflow has always been deeply embedded in the Kubernetes ecosystem. Kubeflow provides a wider selection of infrastructure components out of the box, such as Trainer, Katib, Spark Operator for distributed AI workload orchestration, Notebooks for interactive AI development, Model Registry for artifact management, and KServe for model serving that have been out of scope for Metaflow.

Over the years, Metaflow has delighted end users with its intuitive APIs, while Kubeflow has delivered tons of value to infrastructure teams through its robust platform components. This complementary nature of the tools motivated us to build a bridge between the two: [you can now author projects in Metaflow and deploy them as Kubeflow Pipelines](https://docs.metaflow.org/production/scheduling-metaflow-flows/scheduling-with-kubeflow), side by side with your existing Kubeflow workloads.

# Why Metaflow → Kubeflow

In [the most recent CNCF Technology Radar survey](https://www.cncf.io/wp-content/uploads/2025/11/cncf_report_techradar_111025a.pdf) from October 2025, Metaflow got the highest positive scores in the “*likelihood to recommend*” and “*usefulness*” categories, reflecting its success in providing a set of stable, productivity-boosting APIs for ML/AI developers. 

Metaflow spans the entire development lifecycle—from early experimentation to production deployment and ongoing operations. To give you an idea, the core features below illustrate the breadth of its API surface, grouped by project stage:

## Development

- Straightforward APIs for [creating and composing workflows](https://docs.metaflow.org/metaflow/basics).

- Automated state transfer and management through [artifacts](https://docs.metaflow.org/metaflow/basics#artifacts), allowing you to [build flows incrementally](https://docs.metaflow.org/metaflow/authoring-flows/introduction) and resume them freely (see [a recent article by Netflix](https://netflixtechblog.com/supercharging-the-ml-and-ai-development-experience-at-netflix-b2d5b95c63eb) about the topic)

- Interactive, [real-time visual outputs](https://docs.metaflow.org/metaflow/basics) from tasks through cards \- a perfect substrate for [custom observability solutions, created quickly with AI copilots](https://outerbounds.com/blog/visualize-everything-with-ai).

- Choose the right balance between code and configuration through [built-in configuration management](https://docs.metaflow.org/metaflow/configuring-flows/introduction). 

- Create domain-specific abstractions and project-level policies through [custom decorators](https://docs.metaflow.org/metaflow/composing-flows/introduction).

## Scaling

- [Scale flows horizontally and vertically](https://docs.metaflow.org/scaling/remote-tasks/introduction): Both task and data parallelism are supported.

- [Handle failures gracefully](https://docs.metaflow.org/scaling/failures).

- [Package dependencies automatically](https://docs.metaflow.org/scaling/dependencies) with support for Conda, PyPI, and uv.

- Leverage [distributed computing paradigms](https://docs.metaflow.org/scaling/remote-tasks/distributed-computing) such as Ray, MPI, and Torch Distributed.

- [Checkpoint long-running tasks](https://docs.metaflow.org/scaling/checkpoint/introduction) and manage checkpoints consistently. 

## Deployment

- Maintain a clear separation between experimentation, production, and individual developers through [namespaces](https://docs.metaflow.org/scaling/tagging).

- Adopt CI/CD and GitOps best practices through [branching](https://docs.metaflow.org/production/coordinating-larger-metaflow-projects).

- [Compose large, reactive systems](https://docs.metaflow.org/production/event-triggering) through isolated sub-flows with event triggering.

These features provide a unified, user-facing API for the capabilities required by real-world ML and AI systems. Behind the scenes, Metaflow is built on integrations with production-quality infrastructure, effectively acting as a user-interface layer over platforms like Kubernetes \- and now, Kubeflow. The diagram below illustrates the division of responsibilities:
<img width="3000" height="1687" alt="kubeflow-metaflow-arch" src="https://github.com/user-attachments/assets/88f4af4e-7e27-4287-b275-88e4b1b87449" />


The key benefit of the Metaflow–Kubeflow integration is that it allows organizations to **keep their existing Kubernetes and Kubeflow infrastructure intact, while upgrading the developer experience with higher-level abstractions and additional functionality, provided by Metaflow.**

Currently, the integration supports deploying Metaflow flows as Kubeflow Pipelines. Once you have Metaflow tasks running on Kubernetes, you can access other components such as Katib and Trainer from Metaflow tasks through their Python clients as usual.

# Metaflow → Kubeflow in practice

As the integration requires no changes in your existing Kubeflow infrastructure, it is straightforward to get started. You can [deploy Metaflow in an existing cloud account](https://docs.metaflow.org/getting-started/infrastructure) (GCP, Azure, or AWS) or you can [install the dev stack on your laptop](https://docs.metaflow.org/getting-started/devstack) with a single command.

Once you have Metaflow and Kubeflow running independently, you can install the extension providing the integration (you can [follow instructions in the documentation](https://docs.metaflow.org/production/scheduling-metaflow-flows/scheduling-with-kubeflow)):

```
pip install metaflow-kubeflow
```

The only configuration needed is to point Metaflow at your Kubeflow Pipelines service, either by adding the following line in the Metaflow config or by setting it as an environment variable:

```
METAFLOW_KUBEFLOW_PIPELINES_URL = "http://my-kubeflow"
```

After this, you can author a Metaflow flow as usual and test it locally:

```
python flow.py run
```

which runs the flow quickly as local processes. If everything looks good, you can deploy the flow as a Kubeflow pipeline:

```
python flow.py kubeflow-pipelines create
```

This will package all the source code and dependencies of the flow automatically, compile the Metaflow flow into a Kubeflow Pipelines YAML and deploy it to Kubeflow, which you can see alongside your existing pipelines in the Kubeflow UI. The following screencast shows the process in action:  
[![](https://i.ytimg.com/vi/ALg0A9SzRG8/maxresdefault.jpg)](https://www.youtube.com/watch?v=ALg0A9SzRG8)

The integration doesn’t have 100% feature coverage yet: Some Metaflow features such as [conditional](https://docs.metaflow.org/metaflow/basics#conditionals) and [recursive](https://docs.metaflow.org/metaflow/basics#recursion) steps are not yet supported. In future versions, we may also provide additional convenience APIs for other Kubeflow components, such as KServe \- or you can easily implement them by yourself as [custom decorators](https://docs.metaflow.org/metaflow/composing-flows/custom-decorators) with the [Kubeflow SDK](https://sdk.kubeflow.org/en/latest/)\!

If you want to learn more about the integration, you can watch [an announcement webinar](https://www.youtube.com/watch?v=YDKRIiQNMU0) on Youtube.

## Feedback welcome\!

Like Kubeflow, Metaflow is an open-source project actively developed by multiple organizations — including Netflix, which maintains a dedicated team working on Metaflow, and [Outerbounds, which provides a managed Metaflow platform](https://outerbounds.com) deployed in customers’ own cloud environments.

The Metaflow community convenes at [the Metaflow Slack](http://slack.outerbounds.co). We welcome you to join, ask questions, and give feedback about the Kubeflow integration, and share your wishlist items for the roadmap. We are looking forward to a fruitful collaboration between the two communities\!
