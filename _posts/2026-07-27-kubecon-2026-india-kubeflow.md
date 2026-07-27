---
toc: true
layout: post
comments: true
title: "KubeCon + CloudNativeCon India 2026: Our Kubeflow Community Experience"
hide: false
categories: [kubecon, community]
author: "Khushi Agrawal"
---

## Introduction

![Kubeflow volunteer team at the booth](/images/2026-07-27-kubecon-2026-india-kubeflow/kubecon-india-2026-2.jpg)

KubeCon + CloudNativeCon India 2026 in Mumbai brought together an incredible crowd of developers, maintainers, and cloud-native enthusiasts. The energy throughout the event was inspiring, especially seeing how central AI, machine learning, and MLOps have become within the Kubernetes landscape. (Above image shows part of our volunteer team at the Kubeflow booth, ready to connect with the community.)

This year, Kubeflow had a strong presence at the CNCF Project Pavilion, serving as a central hub for anyone looking to scale AI workloads on cloud-native infrastructure. The conference highlighted the growing adoption of the ecosystem, with a noticeable increase in enterprise users and developers looking to standardize their AI platforms.

This post captures the key takeaways from the booth, the most common architecture questions from the community, and the overall presence of the Kubeflow ecosystem at the event. We hope this gives you a glimpse into the week and encourages you to get involved at future gatherings!

## Featured Talks

- **"Hey AI, Train Llama": Making Kubeflow Agent-Native with MCP**
**Speakers:** [Akash Jaiswal](https://www.linkedin.com/in/akashjaiswal03/) (Oracle), [Abhijeet Dhumal](https://www.linkedin.com/in/abhijeet-dhumal-b6a4a41aa/) (Red Hat)
**Sched Link (Open-Source Summit):** [View on Sched](https://ossindia2026.sched.com/event/2KNF7/hey-ai-train-llama-making-kubeflow-agent-native-with-mcp-akash-jaiswal-oracle-abhijeet-dhumal-red-hat)

<iframe width="100%" height="400" src="https://www.youtube.com/embed/cZ2BP5hQjc8" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

- **When Kubeflow Fights Cilium: Debugging 60% Idle GPUs in Kubernetes**
**Speakers:** [Ramkumar Nagaraj](https://www.linkedin.com/in/ramkumar-nagaraj/), [Bingi Narasimha Karthik](https://www.linkedin.com/in/bingi-narasimha-k/) (Adobe)
**Sched Link:** [View on Sched](https://kccncind2026.sched.com/event/2IW3n/when-kubeflow-fights-cilium-debugging-60-idle-gpus-in-kubernetes-ramkumar-nagaraj-bingi-narasimha-karthik-adobe)

<iframe width="100%" height="400" src="https://www.youtube.com/embed/BG9XGouyM9c" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Kubeflow Booth Highlights

From the moment the exhibition doors opened, the Kubeflow booth was buzzing with activity. We had conversations with a wide mix of attendees, from students looking for their first open-source project to senior platform engineers running large-scale training workloads in production.

![Attendees at the Kubeflow booth](/images/2026-07-27-kubecon-2026-india-kubeflow/kubecon-india-2026-1.jpg)

Here are some of the main takeaways from our time at the booth:

- **From Experimentation to Production:** Many engineers shared how their organizations are moving away from isolated scripts and adopting Kubeflow to standardize their machine learning workflows. We heard stories about teams scaling production pipelines, managing complex deployments, and cutting down model training times.

- **Growing Interest in GenAI and LLMs:** A big portion of our discussions centered around large language models and RAG pipelines. Visitors wanted to know how Kubeflow handles distributed training, model serving, and efficient resource allocation for GPU workloads.

- **Onboarding New Contributors:** We met many developers eager to contribute to the project. We walked them through the repository structure, showed them how to find good first issues on GitHub, and invited them to join our weekly community calls. Several GSoC mentors and active contributors at the booth also shared their firsthand experiences and guidance on getting started.

## Popular Questions from the Audience

**How does end-to-end Kubeflow work?**

Kubeflow is the foundation for AI Platforms on Kubernetes. It provides a composable, modular, and scalable community distribution that covers every stage of the AI lifecycle. We explained how teams can deploy subprojects independently or together, using Kubeflow Notebooks for development, Kubeflow Trainer for scalable LLM fine-tuning, Kubeflow Pipelines (KFP) for automated workflows, and Kubeflow Hub for managing model metadata.

**How is Kubeflow different from MLflow?**

They work best together. Kubeflow [integrates directly with MLflow](https://github.com/kubeflow/mlflow-integration). While MLflow focuses on tracking experiments and registering models, Kubeflow acts as your cloud-native platform foundation, handling the underlying Kubernetes infrastructure, multi-tenant security, and GPU compute resources at scale.

**How can Kubeflow help optimize costs when training LLMs on GPUs?**

With generative AI costs top of mind, visitors wanted to know how to get more out of their hardware. We shared how Kubernetes-native scheduling, resource quotas, and multi-tenancy allow teams to safely share centralized GPU pools. Combined with scale-to-zero serving and spot instance support, organizations can avoid wasting budget on idle compute.

**How does Kubeflow handle pipeline resilience and step failures?**

When training jobs run for hours or days, hardware issues are inevitable. We discussed how Kubeflow Pipelines uses isolated, containerized steps with built-in retry policies and task caching. If a single pod crashes or hits a network issue, the pipeline can automatically recover and resume without losing progress from previously completed steps.

## Our Experience

Volunteering at the Kubeflow booth this year was a lot of fun. Beyond the packed presentation rooms and technical sessions, what stood out was the energy of the people who stopped by. Whether we were troubleshooting a deployment setup for a platform engineer or breaking down MLOps basics for a student, every conversation reminded us why open-source collaboration is so rewarding.

We also had a great time behind the scenes, swapping stories about debugging disasters over coffee breaks while running the booth shifts. Nothing beats getting the community together in person. We hope this motivates more of you to volunteer at future events. You will not want to miss the next one! 😊

A big thank you to everyone who volunteered their time and energy to make the booth a success: [Akash Jaiswal](https://github.com/jaiakash), [Yash Pal](https://github.com/yashpal2104), [Abhijeet Dhumal](https://github.com/abhijeet-dhumal), [Aniket Patil](https://github.com/aniketpati1121), [Rohit Kumar](https://github.com/kmr-rohit), [Khushi Agrawal](https://github.com/khushiiagrawal), [Danish Siddiqui](https://github.com/danish9039), [Digvijay Yeware](https://github.com/digvijay-y), [Kapil Nema](https://github.com/kapil27), [Krishna Gupta](https://github.com/krishna-kg732), [Kunal Dugar](https://github.com/kunal-511), [Yash Agarwal](https://github.com/XploY04), [Milind Dethe](https://github.com/milinddethe15), [Sachin Jha](https://github.com/sachin21212121), and [Valentina Rodriguez Sosa](https://github.com/varodrig) for her ongoing guidance and support. You all made this event special!

![Kubeflow volunteers at the booth](/images/2026-07-27-kubecon-2026-india-kubeflow/kubecon-india-2026-4.jpg)

![Kubeflow team at KubeCon India 2026](/images/2026-07-27-kubecon-2026-india-kubeflow/kubecon-india-2026-3.jpg)

## Want to Help?

The Kubeflow community holds open meetings and is always looking for more volunteers, developers, and users to help shape the future of machine learning on Kubernetes. If you are interested in getting involved, check out the resources below. We would love to build with you!

- Visit the [Kubeflow website](https://www.kubeflow.org/docs/about/community/) or [GitHub repositories](https://github.com/kubeflow).
- Join the [Kubeflow Slack channels](https://www.kubeflow.org/docs/about/community/).
- Subscribe to the [kubeflow-discuss](https://groups.google.com/g/kubeflow-discuss) mailing list.
- To volunteer for future events, join the [#kubeflow-outreach](https://cloud-native.slack.com/?redir=%2Farchives%2FC078ZMRQPB6%3Fname%3DC078ZMRQPB6) channel on the CNCF Slack.
- Attend our weekly [community meeting](https://www.kubeflow.org/docs/about/community/#kubeflow-community-call) to see what we are currently working on.

Feel free to share your thoughts, questions, or KubeCon memories in the comments below. See you at the next event!
