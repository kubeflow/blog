---
toc: true
layout: post
categories: [ trainer ]
comments: true
title: "Democratizing AI Model Training on Kubernetes: Introducing Kubeflow Trainer V2"
hide: false
permalink: /trainer/intro/
author: "Kubeflow Trainer Team"
---

Running machine learning workloads on Kubernetes can be challenging.
Distributed training and LLMs fine-tuning, in particular, involves managing multiple nodes, GPUs, large datasets, and fault tolerance, which often requires deep Kubernetes knowledge.
The **Kubeflow Trainer v2 (KF Trainer)** was created to hide this complexity, by abstracting Kubernetes from AI Practitioners and providing the easiest, most scalable way to run distributed PyTorch jobs.

**The main goals of Kubeflow Trainer v2 include:**
- Make AI/ML workloads easier to manage at scale
- Provide a Pythonic interface to train models
- Deliver the easiest and most scalable PyTorch distributed training on Kubernetes
- Add built-in support for fine-tuning large language models
- Abstract Kubernetes complexity from AI Practitioners
- Consolidate efforts between Kubernetes Batch WG and Kubeflow community

We’re deeply grateful to all contributors and community members who made the **Trainer v2** possible with their hard work and valuable feedback.
We'd like to give special recognition to [andreyvelich](https://github.com/andreyvelich), [tenzen-y](https://github.com/tenzen-y), [electronic-waste](https://github.com/electronic-waste), [astefanutti](https://github.com/astefanutti), [ironicbo](https://github.com/ironicbo), [mahdikhashan](https://github.com/mahdikhashan), [kramaranya](https://github.com/kramaranya), [harshal292004](https://github.com/harshal292004), [akshaychitneni](https://github.com/akshaychitneni), [chenyi015](https://github.com/chenyi015) and the rest of the contributors.
We would also like to highlight [ahg-g](https://github.com/ahg-g), [kannon92](https://github.com/kannon92), and [vsoch](https://github.com/vsoch) whose feedback was essential while we designed the Kubeflow Trainer architecture together with the Batch WG.
See the full [contributor list](https://kubeflow.devstats.cncf.io/d/66/developer-activity-counts-by-companies?orgId=1&var-period_name=Last%206%20months&var-metric=commits&var-repogroup_name=kubeflow%2Ftrainer&var-country_name=All&var-companies=All) for everyone who helped make this release possible.

# Background and Evolution

**Kubeflow Trainer v2** represents the next evolution of the **Kubeflow Training Operator**, building on over seven years of experience running ML workloads on Kubernetes.
The journey began in 2017 when the **Kubeflow** project introduced **TFJob** to orchestrate TensorFlow training on Kubernetes.
At that time, Kubernetes lacked many of the advanced batch processing features needed for distributed ML training, so the community had to implement these capabilities from scratch.

Over the years, the project expanded to support multiple ML frameworks including **PyTorch**, **MXNet**, **MPI**, and **XGBoost** through various specialized operators.
In 2021, these were consolidated into the unified **[Training Operator v1](https://docs.google.com/document/d/1x1JPDQfDMIbnoQRftDH1IzGU0qvHGSU4W6Jl4rJLPhI/edit?tab=t.0#heading=h.e33ufidnl8z6)**.
Meanwhile, the Kubernetes community introduced the **Batch Working Group**, developing important APIs like JobSet, Kueue, Indexed Jobs, and PodFailurePolicy that improved HPC and AI workload management.

**Trainer v2** leverages these Kubernetes-native improvements to make use of existing functionality and not reinvent the wheel.
This collaboration between the Kubernetes and Kubeflow communities delivers a more standardized approach to ML training on Kubernetes.

# User Personas

One of the main challenges with ML training on Kubernetes is that it often requires **AI Practitioners** to have an understanding of **Kubernetes concepts** and the **infrastructure** being used for training. This distracts AI Practitioners from their primary focus.

**The KF Trainer v2** addresses this by **separating the infrastructure configuration from the training job definition**.
This separation is built around three new custom resources definitions (CRDs):
- `TrainingRuntime` - a namespace-scoped resource that contains the infrastructure details that are required for a training job, such as the training image to use, failure policy, and gang-scheduling configuration.
- `ClusterTrainingRuntime` - similar to `TrainingRuntime`, but cluster scoped.
- `TrainJob` - specifies the training job configuration, including the training code to run, config for pulling the training dataset & model, and a reference to the training runtime.

The diagram below shows how different personas interact with these custom resources:

![user_personas](/images/2025-07-09-introducing-trainer-v2/user-personas.drawio.svg)

- **Platform Administrators** define and manage **the infrastructure configurations** required for training jobs using `TrainingRuntimes` or `ClusterTrainingRuntimes`. 
- **AI Practitioners** focus on model development using the simplified `TrainJob` resource or **Python SDK** wrapper, providing a reference to **the training runtime** created by **Platform Administrators**.

# Python SDK

**The KF Trainer v2** introduces a **redesigned Python SDK**, which is intended to be the **primary interface for AI Practitioners**.
The SDK provides a unified interface across multiple ML frameworks and cloud environments, abstracting away the underlying Kubernetes complexity.

The diagram below illustrates how Kubeflow Trainer provides a consistent experience for running ML jobs across different ML frameworks, Kubernetes infrastructures, and cloud providers:

![trainerv2](/images/2025-07-09-introducing-trainer-v2/trainerv2.png)

**Kubeflow Trainer v2** supports multiple ML frameworks through **pre-configured runtimes**. The table below shows the current framework support:

![runtimes](/images/2025-07-09-introducing-trainer-v2/runtimes.png)

The SDK makes it easier for users familiar with Python to **create, manage, and monitor training jobs**, without requiring them to deal with any YAML definitions:

```
from kubeflow.trainer import TrainerClient

client = TrainerClient()

def my_train_func():
    """User defined function that runs on each distributed node process"""
    import os
    import torch
    import torch.distributed as dist
    from torch.utils.data import DataLoader, DistributedSampler
    
    # Setup PyTorch distributed
    backend = "nccl" if torch.cuda.is_available() else "gloo"
    local_rank = int(os.getenv("LOCAL_RANK", 0))
    dist.init_process_group(backend=backend)
    
    # Define your model, dataset, and training loop
    model = YourModel()
    dataset = YourDataset()
    train_loader = DataLoader(dataset, sampler=DistributedSampler(dataset))
    
    # Your training logic here
    for epoch in range(num_epochs):
        for batch in train_loader:
            # Forward pass, backward pass, optimizer step
            ...
            
    # Wait for the distributed training to complete
    dist.barrier()
    if dist.get_rank() == 0:
        print("Training is finished")

    # Clean up PyTorch distributed
    dist.destroy_process_group()

job_name = client.train(
  runtime=client.get_runtime("torch-distributed"),
  trainer=CustomTrainer(
    func=my_train_func,
    num_nodes=5,
    resources_per_node={
      "gpu": 2,
     },
  ),
)

job = client.get_job(name=job_name)

for step in job.steps:
   print(f"Step: {step.name}, Status: {step.status}")

client.get_job_logs(job_name, follow=True)
```
The SDK handles all Kubernetes API interactions. This eliminates the need for AI Practitioners to directly interact with the Kubernetes API.

# Simplified API

Previously, in the **Kubeflow Training Operator** users worked with different custom resources for each ML framework, each with their own framework-specific configurations.
The **KF Trainer v2** replaces these multiple CRDs with a **unified TrainJob API** that works with **multiple ML frameworks**.

For example, here’s how a **PyTorch training job** looks like using **KF Trainer v1**:

```
apiVersion: kubeflow.org/v1
kind: PyTorchJob
metadata:
  name: pytorch-simple
  namespace: kubeflow
spec:
  pytorchReplicaSpecs:
    Master:
      replicas: 1
      restartPolicy: OnFailure
      template:
        spec:
          containers:
            - name: pytorch
              image: docker.io/kubeflowkatib/pytorch-mnist:v1beta1-45c5727
              imagePullPolicy: Always
              command:
                - "python3"
                - "/opt/pytorch-mnist/mnist.py"
                - "--epochs=1"
    Worker:
      replicas: 1
      restartPolicy: OnFailure
      template:
        spec:
          containers:
            - name: pytorch
              image: docker.io/kubeflowkatib/pytorch-mnist:v1beta1-45c5727
              imagePullPolicy: Always
              command:
                - "python3"
                - "/opt/pytorch-mnist/mnist.py"
                - "--epochs=1"
```

In the **KF Trainer v2**, creating an equivalent job becomes much simpler:

```
apiVersion: trainer.kubeflow.org/v1alpha1
kind: TrainJob
metadata:
  name: pytorch-simple
  namespace: kubeflow
spec:
  trainer:
    numNodes: 2
    image: docker.io/kubeflowkatib/pytorch-mnist:v1beta1-45c5727
    command:
      - "python3"
      - "/opt/pytorch-mnist/mnist.py"
      - "--epochs=1"
  runtimeRef:
    name: torch-distributed
    apiGroup: trainer.kubeflow.org
    kind: ClusterTrainingRuntime
```

Additional **infrastructure** and **Kubernetes-specific** details are provided in the referenced **runtime** definition, and managed separately by **Platform Administrators**.
In the future, we might support other runtimes in addition to `TrainingRuntime` and `ClusterTrainingRuntime`, for example [SlurmRuntime](https://github.com/kubeflow/trainer/issues/2249).

# Extensibility and Pipeline Framework

One of the challenges in **KF Trainer v1** was supporting additional ML frameworks, especially for closed-sourced frameworks.
The v2 architecture addresses this by introducing a **Pipeline Framework** that allows Platform Administrators  to **extend the Plugins** and **support orchestration** for their custom in-house ML frameworks.

The diagram below shows Kubeflow Trainer Pipeline Framework overview:

![trainer_pipeline_framework](/images/2025-07-09-introducing-trainer-v2/trainer-pipeline-framework.drawio.svg)

The framework works through a series of phases - **Startup**, **PreExecution**, **Build**, and **PostExecution** - each with **extension points** where custom Plugins can hook in.
This approach allows adding support for new frameworks, custom validation logic, or specialized training orchestration without changing the underlying system.

# LLMs Fine-Tuning Support

Another improvement of **Trainer v2** is its **built-in support for fine-tuning large language models**, where we provide two types of trainers:
- `BuiltinTrainer` - already includes the fine-tuning logic and allows AI Practitioners to quickly start fine-tuning requiring only parameter adjustments.
- `CustomTrainer` - allows users to provide their own training function that encapsulates the entire LLMs fine-tuning.

In the first release, we support **TorchTune LLM Trainer** as the initial option for `BuiltinTrainer`.
For TorchTune, we provide pre-configured runtimes (`ClusterTrainingRuntime`) that currently support `Llama-3.2-1B-Instruct` and `Llama-3.2-3B-Instruct` in the [manifest](https://github.com/kubeflow/trainer/tree/master/manifests/base/runtimes/torchtune/llama3_2).
This approach means that in the future, we can add more frameworks, such as [unsloth](https://github.com/unslothai/unsloth), as additional `BuiltinTrainer` options.
Here's an example using the `BuiltinTrainer` with **TorchTune**:

```
job_name = client.train(
    runtime=Runtime(
        name="torchtune-llama3.2-1b"
    ),
    initializer=Initializer(
        dataset=HuggingFaceDatasetInitializer(
            storage_uri="hf://tatsu-lab/alpaca/data"
        ),
        model=HuggingFaceModelInitializer(
            storage_uri="hf://meta-llama/Llama-3.2-1B-Instruct",
            access_token="<YOUR_HF_TOKEN>"  # Replace with your Hugging Face token,
        )
    ),
    trainer=BuiltinTrainer(
        config=TorchTuneConfig(
            dataset_preprocess_config=TorchTuneInstructDataset(
                source=DataFormat.PARQUET,
            ),
            resources_per_node={
                "gpu": 1,
            }
        )
    )
)
```

This example uses a **builtin runtime image** that uses a foundation Llama model, and fine-tunes it using a dataset pulled from Hugging Face, with the TorchTune configuration provided by the AI Practitioner.
For more details, please refer to [this example](https://github.com/kubeflow/trainer/blob/master/examples/torchtune/llama3_2/alpaca-trainjob-yaml.ipynb).

# Dataset and Model Initializers

**Trainer v2** provides **dedicated initializers** for datasets and models, which significantly simplify the setup process.
Instead of each training pod independently downloading large models and datasets, **initializers handle this once** and **share the data** across all training nodes through a **shared volume**.

This approach saves both **time and resources** by preventing network slowdowns, and **reducing GPU waiting time** during setup by offloading data loading tasks to CPU-based initializers, which preserves expensive GPU resources for the actual training.

# Use of JobSet API

Under the hood, the **KF Trainer v2** uses **[JobSet](https://jobset.sigs.k8s.io/docs/overview/)**, a **Kubernetes-native API** for managing groups of jobs.
This integration allows the KF Trainer v2 to better utilize standard Kubernetes features instead of trying to recreate them.

# Kueue Integration

Resource management is improved through integration with **[Kueue](https://kueue.sigs.k8s.io/)**, a **Kubernetes-native queueing system**.
The KF Trainer v2 includes initial support for Kueue through Pod Integration, which allows individual training pods to be queued when resources are busy.
We are working on **[native Kueue support](https://github.com/kubernetes-sigs/kueue/issues/3884)** for `TrainJob` to provide richer queueing features in future releases.

# MPI Support

The **KF Trainer v2** also provides **MPI v2 support**, which includes **automatic generation of SSH keys** for secure inter-node communication and boosting performance MPI on Kubernetes.

![MPI_support](/images/2025-07-09-introducing-trainer-v2/MPI-support.drawio.svg)

The diagram above shows how this works in practice - the **KF Trainer** automatically **handles the SSH key generation** and **MPI communication** between training pods, which allows frameworks like [DeepSpeed](https://www.deepspeed.ai/) to coordinate training across multiple GPU nodes without requiring manual configuration of inter-node communication.

# Gang-Scheduling

**Gang-scheduling** is an important feature for distributed training that ensures **all pods in a training job are scheduled together** or not at all.
This prevents scenarios where only some pods are scheduled while others remain pending due to resource constraints, which would waste GPU resources and prevent training from starting.

**The KF Trainer v2** provides **built-in gang-scheduling support** through **PodGroupPolicy API**.
This creates **PodGroup resources** that ensure all required pods can be scheduled simultaneously before the training job starts.

**Platform Administrators** can configure gang-scheduling in their **TrainingRuntime** or **ClusterTrainingRuntime** definitions. Here's an example:

```yaml
apiVersion: trainer.kubeflow.org/v1alpha1
kind: ClusterTrainingRuntime
metadata:
  name: torch-distributed-gang-scheduling
spec:
  mlPolicy:
    numNodes: 3
    torch:
      numProcPerNode: 2
  podGroupPolicy:
    coscheduling:
      scheduleTimeoutSeconds: 120
  # ... rest of runtime configuration
```

Currently, **KF Trainer v2** supports the **Co-Scheduling plugin** from [Kubernetes scheduler-plugins](https://github.com/kubernetes-sigs/scheduler-plugins) project.
**[Volcano](https://github.com/kubeflow/trainer/pull/2672)** and **[KAI](https://github.com/kubeflow/trainer/pull/2663)** scheduler support is coming in future releases to provide more advanced scheduling capabilities.

# Fault Tolerance Improvements

Training jobs can sometimes fail due to node issues or other problems. The **KF Trainer v2** improves handling these faults by supporting **Kubernetes PodFailurePolicy**, which allows users to **define specific rules** for handling different types of failures, such as restarting the job after temporary node issues or terminating the job after critical errors.

# What’s Next?

Future enhancements will continue to improve the user experience, integrate deeper with other Kubeflow components, and support more training frameworks.
**Upcoming features** include:
- **[Local Execution](https://github.com/kubeflow/sdk/issues/22)** - run training jobs locally without Kubernetes
- **[Unified Kubeflow SDK](https://docs.google.com/document/d/1rX7ELAHRb_lvh0Y7BK1HBYAbA0zi9enB0F_358ZC58w/edit?tab=t.0#heading=h.e0573r7wwkgl)** - a single SDK for all Kubeflow projects 
- **[Trainer UI](https://github.com/kubeflow/trainer/issues/2648)** - a user interface to expose high level metrics for training jobs and monitor training logs
- **[Native Kueue integration](https://github.com/kubernetes-sigs/kueue/issues/3884)** - improve resource management and scheduling capabilities for TrainJob resources
- **[Model Registry integrations](https://github.com/kubeflow/trainer/issues/2245)** - export trained models directly to Model Registry
- **[Distributed Data Cache](https://github.com/kubeflow/community/pull/864)** - in-memory Apache Arrow caching for tabular datasets
- **[Volcano support](https://github.com/kubeflow/trainer/pull/2672)** - advanced AI-specific scheduling with gang scheduling, priority queues, and resource management capabilities
- **[JAX runtime support](https://github.com/kubeflow/trainer/pull/2643)** - ClusterTrainingRuntime for JAX distributed training
- **[KAI Scheduler support](https://github.com/kubeflow/trainer/pull/2663)** - NVIDIA's GPU-optimized scheduler for AI workloads

# Migration from Training Operator v1

For users migrating from **Kubeflow Training Operator v1**, check out a [**Migration Guide**](https://www.kubeflow.org/docs/components/trainer/operator-guides/migration/).

# Resources and Community

For more information about **Trainer V2**, check out the [Kubeflow Trainer documentation](https://www.kubeflow.org/docs/components/trainer/) and the [design proposal](https://github.com/kubeflow/trainer/tree/master/docs/proposals/2170-kubeflow-trainer-v2) for technical implementation details.

For more details about Kubeflow Trainer, you can also watch our KubeCon presentations:
- [Democratizing AI Model Training on Kubernetes with Kubeflow TrainJob and JobSet](https://youtu.be/Lgy4ir1AhYw)
- [From High Performance Computing To AI Workloads on Kubernetes: MPI Runtime in Kubeflow TrainJob](https://youtu.be/Fnb1a5Kaxgo)

Join the community via the [#kubeflow-trainer](https://www.kubeflow.org/docs/about/community/#kubeflow-slack-channels) channel on CNCF Slack, or attend the [AutoML and Training Working Group](https://docs.google.com/document/d/1MChKfzrKAeFRtYqypFbMXL6ZIc_OgijjkvbqmwRV-64/edit?tab=t.0#heading=h.o8oe6e5kry87) meetings to contribute or ask questions.
Your feedback, contributions, and questions are always welcome!
