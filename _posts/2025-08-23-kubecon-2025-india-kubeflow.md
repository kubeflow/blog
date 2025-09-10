---
toc: true
layout: post
comments: true
title: "KubeCon India 2025 with Kubeflow: Our Community Experience"
hide: false
categories: [kubecon, community]
author: "Akash Jaiswal, Yash Pal"
---

## Introduction

![KubeCon India 2025](/images/2025-08-23-kubecon-2025-india-kubeflow/KubeConIndiaKeynote.png)

KubeCon + CloudNativeCon India 2025 in Hyderabad was an absolute blast! As a second-time attendee ([Akash Jaiswal](https://github.com/jaiakash)) and a first-time attendee ([Yash Pal](https://github.com/yashpal2104)), we couldn't help but be blown away by the incredible energy at one of world's biggest cloud native gatherings. We were super excited seeing Kubeflow get a special shoutout during the opening keynote for its role in cloud native AI/ML and MLOps - definitely made us proud to be part of the community! (Above image shows the keynote moment)

We also got super lucky with the chance to volunteer at the Kubeflow booth this year. We also met [Johnu George](https://github.com/johnugeorge) in person, who delivered two amazing talks on Kubeflow's latest capabilities. It was really exciting to finally meet community members face-to-face whom we've only seen in community calls and Slack!

This blog shares all the exciting bits from our packed 2 days at KubeCon - from awesome booth conversations to technical deep-dives. We hope this motivates more community members to not just contribute but also attend and help Kubeflow at events like KubeCon. Trust me, you won't want to miss the next one! 😊

## Featured Talks

- **Cloud Native GenAI using KServe and OPEA**
**Speakers:** [Johnu George](https://github.com/johnugeorge), Gavrish Prabhu (Nutanix)
**Sched Link:** [View on Sched](https://kccncind2025.sched.com/event/23EtS/cloud-native-genai-using-kserve-and-opea-johnu-george-gavrish-prabhu-nutanix)

<iframe width="100%" height="400" src="https://www.youtube.com/embed/0o8Ng0E1rrA?list=PLj6h78yzYM2MEQTMX_LIOK1hrePHxLD6U" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

- **Bridging Big Data and Machine Learning Ecosystems**
**Speakers:** [Johnu George](https://github.com/johnugeorge), Shiv Jha (Nutanix)
**Sched Link:** [View on Sched](https://kccncind2025.sched.com/event/23Eur/bridging-big-data-and-machine-learning-ecosystems-a-cloud-native-approach-using-kubeflow-johnu-george-shiv-jha-nutanix)

<iframe width="100%" height="400" src="https://www.youtube.com/embed/3NWFCKUhB3A?list=PLj6h78yzYM2MEQTMX_LIOK1hrePHxLD6U" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>


## Kubeflow Booth Highlights

![Kubeflow Booth](/images/2025-08-23-kubecon-2025-india-kubeflow/KubeflowBooth.png)

Here's a picture of our Kubeflow booth volunteer team. It was really great to meet and interact with audiences who had dozens of questions about Kubeflow, contributors who wanted to help, and developers who were already using it and shared their experiences.

Here are some key highlights from our booth conversations:

- **Community Engagement:**
  - Discussions on real-world use cases and deployment strategies. Few users shared their experience of using Kubeflow in their companies and how its benefiting them.
  - Many of audience want to learn more about how to explore and contribute to Kubeflow. (Answers: Join community calls, and check out GitHub for open issues)
  - Several companies expressed interest in adopting projects like Kubeflow. Few senior engineers were already using it for some of their workloads, now they want to use for production workload.

- **Popular Questions from Audience:**
  - How does Kubeflow simplify ML workflows using Kubernetes? Can you clarify why kubeflow is not multicluster agnostic?
  - How does Kubeflow integrate with other cloud-native tools? How is Kubeflow different from other tools in the industry?
  - What are the security considerations for running ML pipelines? How can Kubeflow help optimize costs when working with LLMs, especially in terms of minimizing GPU usage to stay within quota limits while still delivering performance?
  - How mature is Kubeflow today, and how well does it align with the workflows of different MLOps? What is the timeline of graduation for Kubeflow? What does the roadmap for Kubeflow look like?
  - Why has Kubeflow chosen to integrate with ArgoCD rather than Tekton CD — the question that came up from a maintainer of the Tekton project.
- **Popular Questions from Visitors:**
  - How does Kubeflow simplify ML workflows on Kubernetes?
  - How does Kubeflow integrate with other cloud-native tools? Can you clarify why kubeflow is not multicluster agnostic?
  Answer: Kubeflow was originally designed to run within a single Kubernetes cluster, focusing on simplifying ML workflows and providing a unified experience. While some components can be deployed in multiple clusters, Kubeflow itself does not provide built-in, out-of-the-box support for managing resources, pipelines, or workloads across multiple clusters in a transparent or federated way. This is mainly due to the complexity of synchronizing state, security, networking, and resource management across clusters. However, the community is aware of this limitation, and there are ongoing discussions and some third-party tools or custom solutions that attempt to bridge this gap, but true multicluster support is not a core feature as of now.
  - What are the security considerations for running ML pipelines? How is Kubeflow different from other tools?
  - How can Kubeflow help optimize costs when working with LLMs, especially in terms of minimizing GPU usage to stay within quota limits while still delivering performance?
  - How mature is Kubeflow today, and how well does it align with the workflows of different MLOps? What is the timeline of graduation for Kubeflow? What does the roadmap for Kubeflow look like, and how can the community continue to engage and shape its development?
  - Why has Kubeflow chosen to integrate with ArgoCD rather than Tekton CD—a question that even came up from a maintainer of the Tekton project.

## Our experience

What an incredible journey these past two days have been! Beyond the technical talks and booth duties, what really stood out was the genuine excitement around Kubeflow in the community. Seeing users' faces light up when sharing their success stories, or watching newcomers get that "aha!" moment during demos - these are the moments that make community events special.

The technical discussions were mind-blowing too. From hearing how startups are using Kubeflow to train their LLMs, to learning how enterprises are scaling it across thousands of models - each conversation taught us something new. We even got into some heated (but friendly!) debates about MLOps architectures and the future of AI on Kubernetes.

But the best part? The people. Meeting community members we've only known through Slack emojis and GitHub comments to sharing chai/biryani with fellow contributors. These personal connections are what make the open source community truly special. Can't wait for the next one! 🚀

## Want to help?

The Kubeflow community holds open meetings and is always looking for more volunteers and users to unlock the potential of machine learning. If you’re interested in becoming a Kubeflow contributor, please feel free to check out the resources below. We look forward to working with you!

* Visit our [website](https://www.kubeflow.org/docs/about/community/) or [GitHub](https://github.com/kubeflow) page.
* Join the [Kubeflow Slack channels](https://www.kubeflow.org/docs/about/community/).
* Join the [kubeflow-discuss](https://groups.google.com/g/kubeflow-discuss) mailing list.
* Want to volunteer for such events, Join the [kubeflow-outreach](https://cloud-native.slack.com/archives/C078ZMRQPB6) channel on CNCF Slack.
* Attend our weekly [community meeting](https://www.kubeflow.org/docs/about/community/#kubeflow-community-call).

Feel free to share your thoughts or questions in the comments!
