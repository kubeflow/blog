# **Announcing Kubeflow Trainer v2.2 \- JAX & XGBoost Runtimes, Flux HPC Support, and TrainJob progress and metrics observability**

**Author:** Kubeflow Trainer Team

**Date:** March 2026   **Tags:** Release, Kubeflow Trainer, Scheduling, Metrics, HPC

Just a little over one week ahead of Kubecon 2026, the Kubeflow team is excited to ship Trainer v2.2. The v2.2 release reinforces our commitment to expanding the Kubeflow Trainer ecosystem – meeting developers where they are by adding native support for JAX, XGBoost, and Flux, while also delivering deeper observability into training jobs.

Key highlights of the v2.2 release include:

* **First-class support for Training Runtimes** for [JAX](https://www.kubeflow.org/docs/components/trainer/user-guides/jax/) and [XGBoost](https://www.kubeflow.org/docs/components/trainer/user-guides/xgboost/), enabling native distributed training on Kubernetes. This marks a major milestone for the Trainer project, achieving full compatibility with Training Operator v1 CRDs: PyTorchJob, MPIJob, JAXJob, and XGBoostJob – now unified under a single TrainJob abstraction.  
* [**Enhanced training observability**](https://github.com/kubeflow/trainer/tree/master/docs/proposals/2779-trainjob-progress), allowing progress and metrics to be propagated directly from training scripts to the TrainJob status. [Hugging Face Transformers](https://github.com/huggingface/transformers/pull/44487) already integrate with the *KubeflowTrainerCallback* to automate this capability.  
* [**Flux runtime support**](https://www.kubeflow.org/docs/components/trainer/user-guides/flux/), bringing HPC workloads to Kubernetes and improving MPI bootstrapping within TrainJob.  
* [**TrainJob activeDeadlineSeconds API**](https://github.com/kubeflow/trainer/tree/master/docs/proposals/2899-resource-timeouts), enabling explicit timeout policies for training jobs.  
* [**RuntimePatches API**](https://www.kubeflow.org/docs/components/trainer/operator-guides/runtime-patches/), introducing a more flexible and scalable way to customize runtime configurations from the TrainJobs.

You can now install the Kubeflow Trainer control plane and its training runtimes with a single command:

```shell
helm install kubeflow-trainer oci://ghcr.io/kubeflow/charts/kubeflow-trainer \
    --namespace kubeflow-system \
    --create-namespace \
    --version v2.2.0-rc.0 \
    --set runtimes.defaultEnabled=true
```

## **Bringing JAX to Kubernetes with Trainer**

Kubeflow Trainer supports running JAX workloads on Kubernetes through the \`jax-distributed\` runtime. It is designed for distributed and parallel JAX computation using jax.distributed and SPMD primitives like pmap, pjit, and shard\_map. The runtime maps one Kubernetes Pod to one JAX process and injects the required distributed environment variables so training or fine-tuning can run consistently across multiple nodes and devices.  
It supports:

* Multi-process CPU training  
* Multi-GPU training using CUDA enabled JAX  
* Data-parallel and model-parallel JAX workloads  
* Massive scale [TPU distributed training](https://github.com/kubeflow/website/pull/4343) with ComputeClases 

**How to get started:**

Start by following the Getting Started guide for Kubeflow Trainer basics. Then use the jax-distributed runtime and initialize JAX distributed explicitly in your training script before any JAX computation.

Make sure you have kubeflow installed on your machine:

```shell

$pip install kubeflow 
```

## **Technical example:**

```py

from kubeflow.trainer import TrainerClient, CustomTrainer

def get_jax_dist():
    import os
    import jax
    import jax.distributed as dist

    dist.initialize(
        coordinator_address=os.environ["JAX_COORDINATOR_ADDRESS"],
        num_processes=int(os.environ["JAX_NUM_PROCESSES"]),
        process_id=int(os.environ["JAX_PROCESS_ID"]),
    )

    print("JAX Distributed Environment")
    print(f"Local devices: {jax.local_devices()}")
    print(f"Global device count: {jax.device_count()}")

    import jax.numpy as jnp
    x = jnp.ones((4,))
    y = jax.pmap(lambda v: v * jax.process_index())(x)
    print("PMAP result:", y)

client = TrainerClient()
job_id = client.train(
    runtime="jax-distributed",
    trainer=CustomTrainer(func=get_jax_dist),
)
client.wait_for_job_status(job_id)
print("\n".join(client.get_job_logs(name=job_id)))
```

The jax-distributed runtime injects JAX\_NUM\_PROCESSES, JAX\_PROCESS\_ID, and JAX\_COORDINATOR\_ADDRESS into the environment, and all processes must call jax.distributed.initialize() exactly once before any JAX computation. 

For more details, refer to the [Kubeflow Trainer JAX guide](https://www.kubeflow.org/docs/components/trainer/user-guides/jax/) for jax.distributed and SPMD primitives.

## **Bringing XGBoost to Kubernetes with Trainer**

Running distributed XGBoost workloads on Kubernetes has traditionally required manual setup of communication layers, environment variables, and cluster coordination. With this release, Kubeflow Trainer introduces built-in support for XGBoost, enabling seamless distributed training with minimal configuration.

The new xgboost-distributed runtime abstracts away the complexity of setting up XGBoost’s collective communication (Rabit). Trainer automatically provisions worker pods using JobSet and injects the required DMLC environment variables, allowing workers to coordinate and synchronize during training. The rank 0 pod is automatically configured to act as the tracker, simplifying cluster setup even further.

This integration supports both CPU and GPU workloads out of the box. For CPU training, each node runs a single worker leveraging OpenMP for intra-node parallelism. For GPU workloads, each GPU is mapped to an individual worker, enabling efficient scaling across nodes.

For more information, please see this [Notebook example](https://github.com/kubeflow/trainer/blob/master/examples/xgboost/distributed-training/xgboost-distributed.ipynb) and [documentation guide](https://www.kubeflow.org/docs/components/trainer/user-guides/xgboost/).

## **Track TrainJob Progress and Expose Metrics**

In this release, Kubeflow Trainer introduces a powerful new capability to automatically update TrainJob status with real-time training progress and metrics generated directly from your ML code. This enables key insights: such as percentage completion, estimated time remaining (ETA), and training metrics–to be surfaced through the TrainJob API, eliminating the need to manually inspect training logs.

## **How it works**

When this feature is enabled (feature flag TrainJobStatus is required), Kubeflow Trainer starts an HTTP server that exposes endpoints for reporting training progress and metrics. Client applications can send updates to these endpoints, and the TrainJob controller will automatically reflect this information in the job status. Users can then easily access these insights through the Kubeflow SDK without needing to inspect logs.

To simplify adoption, we are collaborating with popular ML frameworks to integrate Kubeflow Trainer callbacks that automate this process. With these integrations, users don’t need to change anything to make it work\!

For example, this functionality is already available in [Hugging Face Transformers](https://github.com/huggingface/transformers/issues/44486), where metrics are automatically reported when using the Trainer.

```py
from transformers import Trainer, TrainingArguments

trainer = Trainer(model=model, args=TrainingArguments(...), train_dataset=ds)
trainer.train()  # Progress automatically reported when running in Kubeflow
```

**Future Plans**

We have an exciting roadmap for this feature, including support for periodic, transparent checkpointing based on ETA, as well as integration with OptimizationJob for hyperparameter tuning jobs.

To learn more about this feature please see [this proposal.](https://github.com/kubeflow/trainer/tree/master/docs/proposals/2779-trainjob-progress)

## **Bringing Flux Framework for HPC and MPI Bootstrapping**

Setting up distributed ML training jobs using MPI can be very time consuming: from stitching together launcher-worker topologies to configuring SSH-based bootstrapping, there’s a lot of moving parts that require code on top of your training code. In v2.2, Kubeflow Trainer brings the Flux Framework – a workload manager that combines hierarchical job management with graph-based scheduling – to handle your HPC-style scheduling needs without the overhead that typically comes with it. 

Flux uses a ZeroMQ to bootstrap MPI, an improvement over traditional SSH, and also brings PMIx and support for more MPI variants. When a training job is submitted, an init container automatically handles Flux’s installation, meaning that you do not need to install Flux to your application container. The plugin also handles cluster discovery, broker configuration, and CURVE certificate generation to provide cryptographic security for the overlay network. 

For teams whose workloads sit at the intersection of ML and HPC, Flux serves as a portability layer that enables running simulation alongside AI/ML workloads. Scheduling to Flux bypasses any potential etcd bottlenecks, and the limitations of the Kubernetes scheduler that require tricks to batch schedule to an underlying single-pod queue. Flux enables fine-grained control over where pods land, and is ideal when you are running simulation pipelines that feed into model Training. This integration also enables the use of Process Management Interface Exascale (PMIx) to manage and coordinate large-scale MPI workloads on Kubernetes using TrainJobs, something that was previously not possible.

**How to get started:**

Before using Flux, read the Getting Started guide to understand the basics of Kubeflow Trainer. Then apply the Flux runtime and a TrainJob manifest. For example:

```shell
kubectl apply --server-side -f https://raw.githubusercontent.com/kubeflow/trainer/refs/heads/master/examples/flux/flux-runtime.yaml
kubectl apply -f https://raw.githubusercontent.com/kubeflow/trainer/refs/heads/master/examples/flux/lammps-train-job.yaml
```

After that, monitor the pods with kubectl get pods \--watch, and inspect the lead broker logs with kubectl logs \<pod-name\> \-c node \-f  , This  also shows how to run the Flux cluster in interactive mode with flux-interactive.yaml, then use kubectl exec and flux proxy to manually run LAMMPS inside the cluster.

The Flux runtime depends on the flux: policy trigger in flux-runtime.yaml, and you can customize the setup through environment variables such as FLUX\_VIEW\_IMAGE and FLUX\_NETWORK\_DEVICE. Binaries are installed under /mnt/flux, software is copied to /opt/software, and configurations are stored in /etc/flux-config. Related documentation includes the Kubeflow Trainer Getting Started guide, the Flux example manifests, and the Flux Framework /HPSF project resources. A simple implementation has been done for this first go, and users are encouraged to submit feedback to request exposure of additional features. A demo video will be showcased at the Kubecon booth for those that can attend.

You can learn more about this in our [Flux Guide](https://www.kubeflow.org/docs/components/trainer/user-guides/flux/).

## **Resource Timeout for TrainJobs**

Previously, TrainJob resources persisted in the cluster indefinitely after completion unless manually removed, which led to Etcd bloat, resource contention and no automatic garbage collection. A job could also get stuck or run indefinitely, wasting CPU/GPU capacity and reducing cluster efficiency. In v2.2, Kubeflow Trainer adds support for spec.active DeadlineSeconds on TrainJob. This field lets users set a hard timeout (in seconds) for a TrainJob’s active execution timeline. When the deadline is exceeded, Trainer marks the TrainJob as Failed (reason: DeadlineExceeded), terminates the running workload, and deletes the underlying JobSet.

## **Technical example:**

There’s a couple ways to specify the timeout limit of a job, the first one is by modifying the TrainJob manifest directly: 

```
apiVersion: trainer.kubeflow.org/v1alpha1
kind: TrainJob
metadata:
	name: quick-experiment
spec:
	activeDeadlineSeconds: 28800 #Max runtime 8 hours
runtimeRef:
	name: torch-distributed-gpu
trainer:
	image: my-training:latest
	numNodes: 2
```

## **Customize Runtime Configs: [RuntimePatchesAPI](https://github.com/kubeflow/trainer/pull/3199)** {#customize-runtime-configs:-runtimepatchesapi}

In many distributed learning environments, multiple controllers can interact with the same TrainJob manifest, making ownership boundaries really important to preserve. The new RuntimePatchesAPI replaces PodTemplateOverrides with a manager-keyed structure that makes it explicit on who applied what and when. 

Each patch is scoped to a named manager and can target specific jobs or pods within the runtime, with both job-level and pod-level overrides supported. The targetJobs field gives you precise control over where a patch lands, if targetJobs is omitted, the patch is applied to the entire JobSet; if targetJobs is set, the patch is applied only to that specific Job within the runtime. This means Kueue can inject node selectors and tolerations into the trainer pod without conflicting with another controller managing job-level metadata, and the full history of what was applied is preserved directly in the spec.

## **Technical example:**

Now in the TrainJob manifest, every manager owns its own entry, pod and job overrides are separate fields under that manager and targetJobs determines whether the patch hits a specific job or the entire JobSet:

```
runtimePatches: 
    # Patch applied to a specific Job within the runtime 
    manager: kueue.x-k8s.io/manager 
    pod: 
        time: "2026-02-17T10:00:00Z" 
        targetJobs: 
            name: trainer # targets only the trainer Job
        spec: 
            nodeSelector: 
                accelerator: nvidia-gpu
```

For cases where a patch needs to apply more broadly across the entire JobSet, the targetJobs field can be omitted entirely:

```
runtimePatches: 
    # Patch applied to the entire JobSet 
    manager: abc.example.com/abc
    job:
        time: "2026-02-17T10:00:00Z"
        metadata:
            labels:
                custom-label: value

```
>[!warning]  This API introduces Breaking Changes!!
>PodTemplateOverrides has been removed in v2.2. If you’re currently using it in your TrainJob manifests, you’ll need to migrate to the RuntimePatches API. 


## **Infrastructure & Breaking Changes**

This release introduces a set of architectural improvements and breaking changes that lay the foundations for a more scalable and modularized Trainer. Please review the following when upgrading to Trainer v2.2:

### **Required: Migrating to RuntimePatchesAPI**

As mentioned above, PodTemplateOverrides has been replaced with RuntimePatchesAPI to support manager-scoped customization and prevent conflicts when multiple controllers are patching the same TrainJob.

If you are using PodTemplateOverrides in your TrainJob manifests or SDK code, you will need to migrate to the manager-keyed RuntimePatches structure. See the [RuntimePatches](#customize-runtime-configs:-runtimepatchesapi) section above for the full API shape and examples. 

### **Required: Remove numProcPerNode from Torch API** 

The numProcPerNode field has been removed from the Torch API. Process-per-node configuration is now handled directly through the runtime, so any TrainJob manifests or SDK calls that set numProcPerNode explicitly will need to be updated before upgrading to v2.2.

### **Required: Remove ElasticPolicy API**

We no longer support the ElasticPolicy API from the MLPolicy as part of Trainer v2.2. If your TrainJobs rely on elastic training configuration through this API, you will need to migrate to the updated approach before upgrading. 

### **TrainJob API fields are now immutable** 

Several TrainJob spec fields are now properly enforced as immutable after job creation. This rejects modifications to fields such as .spec.trainer.image on a running TrainJob upfront instead of having it silently fail at the JobSet controller level. If your workflows rely on updating these fields on a running TrainJob, those updates will now be rejected by the admission webhood. Please review your TrainJob update logic to ensure compatibility with our immutability policies in v2.2. 

## Release Notes

For the complete list of all pull requests, visit the GitHub release page: TBD add release page

## **Roadmap Moving Forward** 

We are excited to continue pushing Kubeflow as a state of the art platform for distributed ML training by making TrainJob manifests more observable and more performant across a wide range of hardware. 

One area we're particularly excited about is bringing Multi-Node NVLink (MNNVL) support for TrainJobs, 
enabling them to treat GPUs across multiple machines as a single unified memory domain. For 
large-scale training, this means significantly faster node-to-node communication compared to 
standard network-based primitives and brings forth a new era of configurations that simply 
weren't practical before on Kubernetes.

On the capacity planning side, we look forward to bringing Predictive GPU Capacity Planning to forecast whether a cluster can actually fulfill a TrainJob before it gets stuck in a queue. This gives teams the training visibility to plan experiments easier, manage costs and avoid wasting time on scheduling things that were never going to happen in the first place. 

A full list of our 2026 roadmap can be found [here](https://github.com/kubeflow/trainer/pull/3242). 

## **Get Involved\!**

The Kubeflow Trainer is built by and for the community. We welcome contributions, feedback, and participation from everyone\! We want to thank the community for their contributions to this release. We invite you to:  
	  
**Contribute:**

* Read the [Contributing Guide](https://github.com/kubeflow/trainer/blob/master/CONTRIBUTING.md).  
* Browse the [good first issues](https://github.com/kubeflow/trainer/issues?q=is%3Aissue%20state%3Aopen%20good%20first%20issues)  
* Explore the [GitHub Repository](https://github.com/kubeflow/trainer)

**Connect with the Community:**

* Join [\#kubeflow-ml-experience](https://cloud-native.slack.com/archives/C08KJBVDH5H) on [CNCF Slack](https://www.kubeflow.org/docs/about/community/#kubeflow-slack-channels)  
* Attend our biweekly [Kubeflow Trainer and katib meetings](https://docs.google.com/document/d/1MChKfzrKAeFRtYqypFbMXL6ZIc_OgijjkvbqmwRV-64/edit?tab=t.0)

**Learn More**

* View the full [Changelog](https://github.com/kubeflow/trainer/blob/master/CHANGELOG.md).

**Headed to [KubeCon](https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/)?** Stop by the Kubeflow booth to see these features in action 😸🧊\!\!

