---
title: "Announcing the Kubeflow Spark Operator: Building a Stronger Spark on Kubernetes Community"
layout: post
toc: false
comments: true
image: 
hide: false
categories: [operators]
permalink: 
author: "<a href='https://www.linkedin.com/in/varaprofile/'>Vara Bonthu</a>, <a href='https://www.linkedin.com/in/yuchaoran/'>Chaoran Yu</a>, <a href='https://www.linkedin.com/in/andrey-velichkevich/'>Andrey Velichkevich</a>, <a href='https://www.linkedin.com/in/wielgusmarcin/'>Marcin Wielgus</a>"
---

We're excited to announce the migration of Google's Spark Operator to
the [Kubeflow Spark Operator](https://github.com/kubeflow/spark-operator),
marking the launch of a significant addition to the [Kubeflow](https://www.kubeflow.org/) ecosystem. The
Kubeflow Spark Operator simplifies the deployment and management of
[Apache
Spark](https://spark.apache.org/docs/latest/index.html)
applications on [Kubernetes](https://kubernetes.io/). This
announcement isn't just about a new piece of technology, it's about
building a stronger, open-governed, and more collaborative community
around Spark on Kubernetes.

## The Journey to Kubeflow Spark Operator

The journey of the Kubeflow Spark Operator began with Google Cloud
Platform's Spark on Kubernetes Operator
(https://cloud.google.com/blog/products/data-analytics/data-analytics-meet-containers-kubernetes-operator-for-apache-spark-now-in-beta).
With over 2.3k stars and 1.3k forks on GitHub, this project laid the
foundation for a robust Spark on Kubernetes experience, enabling users
to deploy Spark workloads seamlessly across Kubernetes clusters.

Growth and innovation require not just code but also community.
Acknowledging the resource and time limitations faced by Google Cloud's
original maintainers, Kubeflow has taken up the mantle.This transition
is not merely administrative but a strategic move towards fostering a
vibrant, diverse, and more actively engaged community.

## Why Kubeflow?

-   **Enhanced Community Engagement:** Transitioning to Kubeflow opens
    the door to a broader developer base, encouraging contributions and
    collaboration. Since Kubeflow is a CNCF incubating project this
    transition will help consolidate Cloud Native and Spark communities
    to work more closely to build robust infrastructure to run Spark
    applications on Kubernetes.

-   **Stronger Governance**: Kubeflow's governance model provides a
    structured environment for decision-making and project management,
    ensuring sustainable growth for the Spark Operator.

-   **Unified Ecosystem**: By bringing the Spark Operator under the
    Kubeflow umbrella, we're not just merging projects; we're building
    a cohesive ecosystem that enhances the Spark on Kubernetes
    experience.

-   **Integration with AI/ML:** Kubeflow provides several components to
    address many stages of the AI/ML lifecycle. The Spark distributed
    data processing capabilities are a natural expansion, allowing the
    Spark community to closely collaborate and better integrate within
    the end-to-end ML lifecycle.

## What's Next?

We are dedicated to not just maintaining but enhancing the Kubeflow
Spark Operator for the long term. Here's what you can look forward to:

-   **Upcoming roadmap**: As part of the first release, we aim to update
    the documentation with references to Kubeflow, address GitHub
    workflow issues, and update the container registry with Kubeflow,
    along with any other critical issues.

-   **Ongoing Support and Enhancements**: At the time of migration to
    the Kubeflow repository, the repository comprised 450+ issues and
    60+ pull requests. We kindly request contributors to rebase their
    code and update the PR with a comment indicating its continued
    relevance. As for open issues, they will be considered for
    resolution as the broader community and contributors engage in
    upcoming releases.The operator will continue to evolve,
    incorporating new features and improvements to stay at the forefront
    of Kubernetes deployments.

-   **Rich Community Resources**: From detailed documentation to
    hands-on tutorials, we're crafting resources to help you succeed
    with the Spark Operator. We are planning to host regular Spark
    Operator calls to discuss users issues, questions, and future
    roadmaps.

-   **Open Doors for Contributions**: This is a call to arms for
    developers, writers, and enthusiasts! Your contributions are the
    lifeblood of this project, and there's a place for everyone to make
    a mark.

-   **Kubeflow Working Group Data:** To consolidate efforts around new
    data tools in the Kubeflow ecosystem such as Spark Operator and
    Model Registry the new Working Group Data will be formalized soon.
    Feel free to review [this PR](https://github.com/kubeflow/community/pull/673) to
    get involved and provide your feedback on the charter.

## Join the Movement

The Kubeflow Spark Operator is more than just software. It's a
community endeavor. Here's how you can be a part of this journey:

-   **Dive In**: Visit our [GitHub repository](https://github.com/kubeflow/spark-operator)
    to start your journey with the Kubeflow Spark Operator.

-   **Contribute**: Every code snippet, documentation update, and piece
    of feedback counts. Find out how you can contribute on GitHub.

-   **Be Part of the Community**: Join the [CNCF Slack Workspace](https://www.kubeflow.org/docs/about/community/#kubeflow-slack-channels) 
    and then join the conversation in the ```#kubeflow-spark-operator``` Channel. 
    Whether you're seeking advice, sharing insights, or just listening in, 
    your presence enriches us. Follow [this guide](https://www.kubeflow.org/docs/about/community/)
    to learn more about Kubeflow community.

-   **Kubeflow Spark Operator Community Call**: We're excited to announce Spark Operator Community Monthly Meetings for Open Source Contributors starting **May 17th, 2024 (10-11 AM PST)**. These meetings, held every third Friday, are your chance to discuss project updates, share ideas, and collaborate with the community. You can find the Zoom call details and meeting notes in this [Google Doc](https://docs.google.com/document/d/1AnG6ptKLBY7O6ddyNm4SVsEbfu6jiyVyN3hDDgDUnxQ/edit#heading=h.pgrbsx5c3qqo). Please also join the [#kubeflow-discuss](https://www.kubeflow.org/docs/about/community/#kubeflow-mailing-list) Google group and find meeting links in the ```#kubeflow-spark-operator``` channel (You will need to join [CNCF Slack Workspace](https://www.kubeflow.org/docs/about/community/#kubeflow-slack-channels)). 


In the spirit of collaboration fostered on platforms like Slack, and
with the generous support of the Google Cloud team, we're set to sail
into a promising future. The Kubeflow Spark Operator isn't just a tool,
it's our collective step towards harnessing the true potential of Spark
on Kubernetes. Together, let's shape the future of cloud-native big
data processing.

**_Reference Issues_**

-   [Action items for adoption of Spark Kubernetes Operator in Kubeflow](https://github.com/kubeflow/spark-operator/issues/1928#issue-2066490838)

-   [WG Data(name provisional)proposal](https://github.com/kubeflow/community/pull/673)

-   [Update Documentation: Redirect Helm Chart Installation Links to Kubeflow Repository](https://github.com/kubeflow/spark-operator/issues/1929)

-   [Update Release Workflows: Change Container Registry to Kubeflow's ghcr.io](https://github.com/kubeflow/spark-operator/issues/1930)