---
toc: true
layout: post
comments: true
title: "GSoC 2025: Meet Our Projects and Contributors 🚀"
hide: false
categories: [gsoc, community, kubeflow]
author: "Kubeflow Outreach Team"
---

## Introduction

Google Summer of Code (GSoC) 2025 has been an exciting journey for the Kubeflow community! We are very grateful for Google and the open source community for their commitment, dedication and efforts.🎉  
This year, 9 contributors from around the world collaborated with mentors to improve different parts of the Kubeflow ecosystem — from infrastructure and CI/CD, to notebooks, ML workflows, and beyond.

In this blog, we’re highlighting all the projects that were part of **GSoC 2025**, their goals, the impact they’ve created, and the amazing contributors behind them.  

👉 You can explore the full list on our [GSoC 2025 page](https://www.kubeflow.org/events/gsoc-2025/).

---

## 📚 Project Highlights

Below are the projects from this year’s GSoC. Each section includes a short summary, contributor details, and links to project resources.

---

### Project 1: Kubeflow Platform Enhancements
**Contributor:** Harshvir Potpose ([@akagami-harsh](https://github.com/akagami-harsh))
**Mentors:** Julius von Kohout ([@juliusvonkohout](https://github.com/juliusvonkohout))

**Overview:**  
MinIO transitioned to the AGPLv3 license in 2021, creating significant compliance challenges for Kubeflow Pipelines. The AGPL's copyleft provisions require that any software linking to AGPL-licensed components must also adopt the AGPL license, effectively preventing KFP from upgrading to newer MinIO versions without changing its own licensing model.

This project addressed this critical blocker by implementing SeaweedFS as a production-ready replacement for MinIO. SeaweedFS offers a more permissive Apache 2.0 license while providing superior performance characteristics and enterprise-grade reliability.

**Key Outcomes:**  
- Successfully migrated to SeaweedFS as a secure replacement for MinIO and integrated it into Kubeflow Pipelines
- Eliminated MinIO's licensing constraints by adopting SeaweedFS's more permissive license model
- Implemented comprehensive CI tests for SeaweedFS deployment and namespace isolation functionality
- Strengthened the manifests repository's CI pipeline and contributed to the dashboard migration efforts
- Enforcing PodSecurityStandars baseline/restricted

**Resources:**  
- 📄 [Project Page](https://summerofcode.withgoogle.com/programs/2025/projects/PWDq4Zvt)  
- ✍️ [Personal Blog: Kubeflow Pipelines Embraces SeaweedFS](https://medium.com/@hpotpose26/kubeflow-pipelines-embraces-seaweedfs-9a7e022d5571)  

---

### 2. Project Title 2  
**Contributor:** Name (GitHub: [@username](https://github.com/username))  
**Mentors:** Mentor Name(s)  

**Overview:**  
Brief description of the project.

**Key Outcomes:**  
- Item 1  
- Item 2  
- Item 3  

**Resources:**  

- 📄 [Project Repo](#)  
- ✍️ [Blog](#)  

---

### Project 4: Deploying Kubeflow with Helm Charts

**Contributor:** Kunal Dugar ([@kunal-511](https://github.com/kunal-511))  
**Mentors:** Julius von Kohout ([@juliusvonkohout](https://github.com/juliusvonkohout)), Valentina Rodriguez Sosa ([@varodrig](https://github.com/varodrig)), Chase Cadet ([@Chasecadet](https://github.com/Chasecadet))

**Overview:**  
This project focused on creating component-based Helm charts for Kubeflow, enabling flexible and incremental deployment of ML infrastructure. Instead of requiring a full platform installation, users can now deploy specific components like Katib, Pipelines, Model Registry, and others independently with customized configurations.

**Key Outcomes:**  
- Kubeflow AI reference paltform end to end testing
- Created production-ready Helm charts for Katib, Model Registry, KServe Web App, Notebook Controller, and Kubeflow Pipelines—enabling one-command deployment of individual components
- Built automated testing infrastructure with diff tools to validate Helm charts against Kustomize manifests, ensuring accuracy and catching regressions quickly
- Enabled incremental Kubeflow adoption, reducing deployment complexity from days to hours for organizations building production ML platforms

**Resources:**  
- 📄 [Project Page](https://summerofcode.withgoogle.com/programs/2025/projects/)  
- 🧩 [Kubeflow Enhancement Proposal (KEP)-831-Kubeflow-Helm-Support: Support Helm as an Alternative for Kustomize](https://github.com/kubeflow/community/pull/832)  
- ✍️ [Blog: My GSoC Journey: Deploying Kubeflow with Helm Charts](https://medium.com/@kunalD02/my-gsoc-journey-deploying-kubeflow-with-helm-charts-e7f9dea7b56e)

---

### Project 7: GPU Testing for LLM Blueprints

**Contributor:** Akash Jaiswal ([@jaiakash](https://github.com/jaiakash))  
**Mentors:** Andrey Velichkevich ([@andreyvelich](https://github.com/andreyvelich)), Valentina Rodriguez Sosa([@varodrig](https://github.com/varodrig))

![Diagram](/images/2025-09-06-kubeflow-and-gsoc2025/project7.png)

**Overview:**  
We had a few examples in the repository that we wanted to include in our end-to-end (E2E) tests, but all of them were CPU-based. Projects like Torchune and Qwen 2.5, for instance, require GPU resources to run — yet our existing CI setup couldn’t validate them at all because it was entirely CPU-focused.

This created a major gap: whenever someone contributed a new LLM example or modified the trainer logic, we had no automated way to verify if those changes would work in a GPU environment — the same environment where these workloads are actually deployed in production.

The goal of this project was to add CI with GPU support directly into our CI/CD workflow.

**Key Outcomes:**  

- Integrating GPU runners into GitHub Actions so that any pull request could automatically trigger GPU-backed E2E tests.

- Making the setup scalable and cost-efficient — instead of maintaining expensive GPU machines 24/7, we needed an on-demand system that provisions GPU resources only when a test is triggered.

**Resources:**  

- 📄 [Project Page](https://summerofcode.withgoogle.com/programs/2025/projects/fwZkvPr0)
- 🧩 [Kubeflow Enhancement Proposal (KEP)](https://github.com/kubeflow/trainer/pull/2689)  
- ✍️ [Personal Blog: Scaling GPU Testing for LLM Blueprints](https://my-experience-with-kubeflow-for-gsoc.hashnode.dev/gsoc-2025-with-kubeflow-scaling-gpu-testing-for-llm-blueprints)

---

### Project 10: Support Volcano Scheduler in Kubeflow Trainer
**Contributor:** Xinmin Du (GitHub: [@Doris-xm](https://github.com/Doris-xm))  
**Mentors:** Shao Wang ([@Electronic-Waste](https://github.com/Electronic-Waste)), Yuchen Cheng([@rudeigerc](https://github.com/rudeigerc))

**Overview:**  
The project aims to integrate the **Volcano scheduler** into Kubeflow Trainer as a **runtime plugin**.
This will allow users to take advantage of advanced AI-specific scheduling features, such as Gang Scheduling and priority scheduling, supported by Volcano.

**Key Outcomes:**
- Integrate the **Volcano** scheduler into Trainer as a runtime plugin to support Gang Scheduling and resource management for distributed training jobs.
- Enabled AI-specific features such as priority scheduling, queue-based management, and network topology–aware scheduling.

**Resources:**

- 📄 [Project Page](https://summerofcode.withgoogle.com/programs/2025/projects/ZWbY1Rfj)
- 🧩 [Kubeflow Enhancement Proposal (KEP)](https://github.com/kubeflow/trainer/pull/2672)

---

## 🎉 Wrapping Up

We’re proud of what our GSoC 2025 contributors achieved and the impact they’ve made on the Kubeflow ecosystem. Their work not only strengthens existing components but also lays the foundation for future innovation in MLOps and AI infrastructure.

A huge **thank you** 🙏 to all contributors, mentors, and community members who made this program a success!

---

## 👩‍💻 Want to Get Involved?

The Kubeflow community is open to contributors of all backgrounds and skill levels. Whether you’re passionate about ML infrastructure, frontend, DevOps, or documentation — there’s a place for you here.

- 💻 Visit our [website](https://www.kubeflow.org/docs/about/community/) and [GitHub](https://github.com/kubeflow)
- 💬 Join our [Slack](https://www.kubeflow.org/docs/about/community/)
- 🗓️ Attend the [community calls](https://www.kubeflow.org/docs/about/community/#kubeflow-community-call)
- 📩 Subscribe to the [kubeflow-discuss](https://groups.google.com/g/kubeflow-discuss) mailing list

Let’s continue building the future of MLOps together 🚀
