---
layout: post
title: "Integrating Kubeflow Model Registry into Your Kubeflow Pipelines"
author: "Hailey Purdom" # Your Name
date: 2025-07-25 # Use the date you want to appear
categories: # Add relevant categories/tags for the blog post
  - mlops
  - pipelines
  - model-registry
  - kubeflow
tags:
  - mlops
  - kubeflow
  - pipelines
  - model-registry
  - kind
  - tutorial
---



# Integrating Kubeflow Model Registry into Your Kubeflow Pipelines





# Introduction: Centralizing Your ML Models with Kubeflow

In the journey of Machine Learning Operations (MLOps), managing trained models effectively is as crucial as building them. While Kubeflow Pipelines (KFP) provides powerful orchestration for your ML workflows, the Kubeflow Model Registry steps in as the centralized hub for versioning, cataloging, and discovering your machine learning models.

This blog post will serve as a practical guide, walking you through the process of integrating the Kubeflow Model Registry directly into your KFP pipelines. We'll cover the benefits, best practices for model registration, and provide a hands-on example, drawing from real-world troubleshooting steps encountered during setup on a local kind cluster.



# Why Leverage Model Registry in Your Pipelines?

**Integrating model registration as a native step within your Kubeflow Pipelines offers significant advantages for robust MLOps:**

- Centralized Cataloging: Move beyond scattered model files. The Model Registry provides a single source of truth for all your models, making them easily discoverable across your organization.

- Structured Versioning & Lineage: Automatically track different iterations of your models. Each model version can be linked back to the exact pipeline run that produced it, ensuring full traceability and reproducibility.

- Enhanced Governance & Auditability: Maintain a clear record of model lifecycles, crucial for compliance and auditing.

- Seamless Handover to Serving: Registered models can be easily referenced by model serving platforms like KServe (formerly KFServing), streamlining deployment and management.

- Automated Workflow: Eliminate manual steps. Once a model passes evaluation within a pipeline, it can be automatically registered, reducing human error and accelerating deployment.



You'd typically want to register a model from a pipeline when it has met predefined performance criteria, passed validation, and is ready to be shared, deployed, or archived.

# Models vs. Model Versions: A Key Distinction

Understanding the core entities in the Model Registry is fundamental:

- Registered Model: This represents the conceptual model. Think of it as a logical grouping for all iterations of a particular ML solution (e.g., "Fraud Detection Classifier," "Customer Churn Predictor").

- Model Version: This is a specific iteration or snapshot of a Registered Model. Each version is immutable and holds unique artifacts, metadata, and a precise lineage (e.g., "v1.0.0," "v1.0.1-retrained," "v2025-07-18-production").

# Getting Started: Setting Up Your Local Kubeflow Environment

To follow this guide, you'll need a local Kubernetes cluster with Kubeflow Pipelines and the Kubeflow Model Registry deployed. We'll use [kind](https://kind.sigs.k8s.io/) (Kubernetes in Docker) for this setup.


**Prerequisites**

* A container engine (e.g., [Docker](https://docs.docker.com/get-docker/)).
* [Python](https://www.python.org/downloads/) (3.11 or newer).
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/): Kubernetes command-line tool.
* [kind](https://kind.sigs.k8s.io/docs/user/quick-start/): Kubernetes in Docker.
* [helm](https://helm.sh/docs/intro/install/): Kubernetes package manager.
* [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git): For cloning repositories.
- **Install Kustomize:**
Kustomize is a standalone tool for customizing Kubernetes configurations. It's essential for applying the manifests in this guide.
```
curl -Lo kustomize.tar.gz https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2Fv5.7.1/kustomize_v5.7.1_linux_amd64.tar.gz
tar -xzvf kustomize.tar.gz
mv kustomize ~/bin # Or /usr/local/bin if you prefer a system-wide install
chmod +x ~/bin/kustomize
rm -f kustomize.tar.gz
# Ensure ~/bin is in your PATH, or if moved to /usr/local/bin, it's already in PATH.
# Perform a full system logout and login after installation to refresh PATH.
```

 # Common Troubleshooting during Setup:
Setting up complex MLOps tools locally can be challenging. Here, we provide the robust deployment steps, incorporating solutions for common issues encountered during this process:

- `kind` Cluster Instability / DNS Issues (`ImagePullBackOff, Temporary failure in name resolution, nf_conntrack_ipv4 not found`): These often stem from conflicts with your host's Docker networking, VPNs, or missing kernel modules.
- **Solution:** Aggressive Docker/`kind` cleanup (`sudo docker system prune -a --volumes -f`), ensuring `kind` is installed correctly (refer to `kind`'s [installation guide](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)), and a full system logout/login to refresh the environment.

- KFP Core Component Crashes (`metadata-grpc-deployment CrashLoopBackOff` with `Exit Code 139` - Segmentation Fault): This often indicates an incompatibility between the `ml_metadata_store_server` image and your host's kernel.

- **Solution:** Patch the local KFP manifests to use an older, more compatible image version (e.g., `1.13.0` or `1.12.0`) in `~/kfp-local-manifests/manifests/kustomize/base/metadata/base/metadata-grpc-deployment.yaml.`

- PersistentVolumeClaim (PVC) `Pending`: This means the cluster's local storage provisioner isn't working.

- **Solution:** A full `kind` and Docker reset (`sudo systemctl stop docker, sudo systemctl start docker`) often resolves this by restarting the `kind`'s default local path provisioner.

- "Pipeline version creation failed" / "Cannot find context" in KFP UI: These are symptoms of KFP's core components (especially ML Metadata and the KFP API server) not being fully `Running` and `READY`.

- **Solution:** Patience and verifying `kubectl get pods -n kubeflow` are key.

- Model Registry Pods Missing / `CreateContainerConfigError`: This usually indicates a configuration problem preventing the container from starting. While transient network issues can sometimes cause similar symptoms, for `CreateContainerConfigError`, a manifest fix is often needed. If persistent, ensure your Model Registry deployment manifests (e.g., from your cloned repository) are up-to-date, as an outdated fork might lead to incompatibilities with other Kubeflow components. We found success deploying the Model Registry using its Kustomize manifests from the `kubeflow/model-registry` repository's `overlays/db` directory.

- `Model_registry.exceptions.StoreError: Version X already exists`: This error occurs when you try to register a model version with a `model_name` and `model_version_name `combination that already exists in the Model Registry.
- **Solution:** This indicates the Model Registry is working as intended! Simply provide a new, unique `model_version_name` for your pipeline run (e.g., `v1.0.1`, `v2.0.0`, or `v1.0.0-run-timestamp`).


# Deployment Steps:

Install `kind` (if not already installed via dnf):

```
sudo dnf install kind # Recommended for Fedora
# OR manual install if dnf fails (e.g., if 'No match for argument: kind'):
# cd ~
# curl -Lo kind https://kind.sigs.k8s.io/dl/v0.22.0/kind-linux-amd64
# chmod +x kind
# sudo mv kind /usr/local/bin/kind
# Perform a full system logout and login after any kind installation/update.
```

Clone Kubeflow Pipelines Repository:
```
cd ~ git clone https://github.com/kubeflow/pipelines.git kfp-local-manifests
```



If you needed to patch `metadata-grpc-deployment.yaml` for image compatibility (e.g., changing `ml_metadata_store_server:1.14.0` to `1.13.0` for `Exit Code 139` fix), do it now in `~/kfp-local-manifests/manifests/kustomize/base/metadata/base/metadata-grpc-deployment.yaml.`

Deploy Kubeflow Pipelines on `kind`(Recommended Method): ***This `make` target automates the `kind` cluster creation and KFP deployment using the `platform-agnostic` manifests.***
```
cd ~/kfp-local-manifests/backend # Navigate to the backend directory
make kind-cluster-agnostic
```


***Note:*** This command will create the `kind` cluster (if it doesn't exist), deploy all necessary KFP components, and wait for core deployments (MySQL, MLMD, KFP API) to become available. This process can take 10-20 minutes or more. Monitor its output carefully.


Troubleshooting `make kind-cluster-agnostic`: 
If you encounter "No rule to make target" or other errors, ensure your `kubeflow/pipelines` repository clone is up-to-date and contains this target in `backend/Makefile`.

Verify KFP Health:
- After `make kind-cluster-agnostic` finishes, open a new terminal.
- Run this command repeatedly until ALL (or almost all) pods in the `kubeflow` namespace are `Running` and `READY` `1/1`.

```
kubectl get pods -n kubeflow
```

- ***This is crucial. Do not proceed until KFP is healthy.***


Clone Kubeflow Model Registry Repository:
```
cd ~
git clone https://github.com/kubeflow/model-registry.git
```

Deploy Kubeflow Model Registry (API Server): This deploys the Model Registry API server, which stores and serves model metadata.
```
cd ~/model-registry/manifests/kustomize/overlays/db # Navigate to the correct overlay for embedded DB
kubectl apply -k . -n kubeflow
```


- Troubleshooting Model Registry Pods: Wait for `model-registry-deployment pod` to become `Running` and `READY` (`kubectl get pods -n kubeflow | grep model-registry`).

**Install and Deploy Kubeflow Model Registry UI:**
/ The Model Registry UI is a separate frontend application that provides a browsable interface to your registered models. There are two primary ways to deploy it: a simpler method for basic setups, and a more comprehensive method for multi-user Kubeflow environments.

- **Option A:** Basic UI Deployment (Recommended for simplicity with standalone KFP): This method deploys the UI without requiring Istio or other multi-user components.

Installation (Cloning the `kubeflow/manifests` repository, pinned to a compatible release): First, clone the [Kubeflow manifests repository](https://github.com/kubeflow/manifests), (if you haven't already). We recommend pinning to a specific release (e.g., v1.7.0) compatible with KFP 2.5.0.
```
cd ~
git clone https://github.com/kubeflow/manifests.git kubeflow-manifests-repo # Clone to a distinct name
cd kubeflow-manifests-repo
git fetch --tags
git checkout tags/v1.7.0 # Pin to Kubeflow manifests v1.7.0 (compatible with KFP 2.5.0)
```

- Deployment (Applying manifests): Navigate to the Model Registry UI `base` overlay:
```
cd ~/kubeflow-manifests-repo/applications/model-registry/upstream/options/ui/base # Using 'base' overlay for non-Istio
```

Apply the UI manifests:
```
kubectl apply -k . -n kubeflow
```

Wait for the UI pod to be ready:
```
kubectl get pods -n kubeflow -l app=model-registry-ui
```

- **Option B:** Multi-User Kubeflow Deployment (More comprehensive, but complex): This option deploys a full multi-user Kubeflow environment, which includes Istio, Dex, and other components necessary for authentication and traffic management. This path is significantly more time-consuming and complex to set up, but it enables the Model Registry UI to integrate with the Central Dashboard in a production-like, authenticated manner.

***Note:*** This is a major deployment effort that goes beyond the scope of a simple Model Registry integration. It involves deploying many components from the root of the `kubeflow/manifests` repository. The exact steps are detailed in the [Kubeflow manifests README](https://github.com/kubeflow/manifests) under the "Deploy Kubeflow in Multi-User Mode" section.

**Steps (summary from `kubeflow/manifests` README):**
- Create the Kind cluster (if not already done).
- Install [cert-manager](https://cert-manager.io/docs/installation/kubernetes/).
- Install [Istio](https://istio.io/latest/docs/setup/getting-started/).
- Install [Oauth2-proxy](https://oauth2-proxy.github.io/oauth2-proxy/installation/).
- Install [Dex](https://dexidp.io/docs/getting-started/) (skip identity provider connection for basic setup).
- Deploy Kubeflow Namespace, Roles, and Istio Resources.
- Install Kubeflow Pipelines (full version).
- Install Central Dashboard.
- Configure Profiles + KFAM (Kubeflow Access Management).
- Configure User Namespaces.

**The following `install.sh script`, developed by Matt Prahl, automates the complex, multi-component Kubeflow deployment stated above on Kind.**
```
    #!/bin/bash
    set -euo pipefail

    # Prior to running this, consider setting the /etc/sysctl.d/99-inotify.conf file to:
    # fs.inotify.max_user_watches = 524288
    # fs.inotify.max_user_instances = 1024

    # Then run sudo sysctl --system to apply the change

    # Check if there's already a Kind cluster running
    if kind get clusters | grep -q .; then
        echo "Error: There is already a Kind cluster running. Please delete it first with:"
        echo "  kind delete clusters --all"
        exit 1
    fi

    cat <<EOF | kind create cluster --name=kubeflow --config=-
    kind: Cluster
    apiVersion: kind.x-k8s.io/v1alpha4
    nodes:
    - role: control-plane
      image: kindest/node:v1.32.0@sha256:c48c62eac5da28cdadcf560d1d8616cfa6783b58f0d94cf63ad1bf49600cb027
      kubeadmConfigPatches:
      - |
        kind: ClusterConfiguration
        apiServer:
          extraArgs:
            "service-account-issuer": "[https://kubernetes.default.svc](https://kubernetes.default.svc)"
            "service-account-signing-key-file": "/etc/kubernetes/pki/sa.key"
    EOF

    echo "Install cert-manager"
    # Retry loop for cert-manager installation
    retry_count=0

    while true; do
        retry_count=$((retry_count + 1))
        echo "Attempting to install cert-manager (attempt $retry_count)"

        # Try both commands
        if kustomize build common/cert-manager/base | kubectl apply -f - && \
           kustomize build common/cert-manager/kubeflow-issuer/base | kubectl apply -f -; then
            echo "Cert-manager installation successful!"
            break
        else
            echo "Cert-manager installation failed. Waiting 5 seconds before retry..."
            sleep 5
        fi
    done

    echo "Installing Istio CNI configured with external authorization..."
    kustomize build common/istio/istio-crds/base | kubectl apply -f -
    kustomize build common/istio/istio-namespace/base | kubectl apply -f -
    kustomize build common/istio/istio-install/overlays/oauth2-proxy | kubectl apply -f -

    echo "Installing oauth2-proxy..."
    kustomize build common/oauth2-proxy/overlays/m2m-dex-only/ | kubectl apply -f -
    kubectl wait --for=condition=Ready pod -l 'app.kubernetes.io/name=oauth2-proxy' --timeout=180s -n oauth2-proxy

    echo "Installing Dex..."
    kustomize build common/dex/overlays/oauth2-proxy | kubectl apply -f -
    kubectl wait --for=condition=Ready pods --all --timeout=180s -n auth

    echo "Creating Kubeflow namespace..."
    kustomize build common/kubeflow-namespace/base | kubectl apply -f -

    echo "Creating Istio resources..."
    kustomize build common/istio/kubeflow-istio-resources/base | kubectl apply -f -

    echo "Installing KFP..."
    # Retry loop for KFP installation
    retry_count=0

    while true; do
        retry_count=$((retry_count + 1))
        echo "Attempting to install KFP (attempt $retry_count)"

        if kustomize build applications/pipeline/upstream/env/cert-manager/platform-agnostic-multi-user | kubectl apply -f -; then
            echo "KFP installation successful!"
            break
        else
            echo "KFP installation failed. Waiting 5 seconds before retry..."
            sleep 5
        fi
    done

    echo "Installing the dashboard..."
    kustomize build common/kubeflow-roles/base | kubectl apply -f -
    kustomize build applications/centraldashboard/overlays/oauth2-proxy | kubectl apply -f -

    echo "Installing profiles..."
    kustomize build applications/profiles/upstream/overlays/kubeflow | kubectl apply -f -

    echo "Setting up the user namespace..."
    kustomize build common/user-namespace/base | kubectl apply -f -

    echo "Waiting for the kubeflow-user-example-com namespace to be created..."
    # Retry loop for namespace creation
    retry_count=0

    while true; do
        retry_count=$((retry_count + 1))
        echo "Checking for namespace kubeflow-user-example-com (attempt $retry_count)"

        if kubectl get namespace kubeflow-user-example-com >/dev/null 2>&1; then
            echo "Namespace kubeflow-user-example-com found!"
            kubectl get namespace kubeflow-user-example-com
            break
        else
            echo "Namespace not found yet. Waiting 5 seconds before retry..."
            sleep 5
        fi
    done

    echo "Deploying Model Registry..."
    kubectl apply -k applications/model-registry/upstream/overlays/db -n kubeflow-user-example-com
    kubectl apply -k applications/model-registry/upstream/options/istio -n kubeflow-user-example-com

    echo "Waiting for Model Registry..."
    kubectl wait --for=condition=available -n kubeflow-user-example-com deployment/model-registry-deployment --timeout=2m

    echo "Deploying Model Registry UI..."
    kubectl apply -k applications/model-registry/upstream/options/ui/overlays/istio
    # Update central dashboard config to add Model Registry menu item
    kubectl get configmap centraldashboard-config -n kubeflow -o json | \
      jq '.data.links |= (fromjson | .menuLinks += [{"icon": "assignment", "link": "/model-registry/", "text": "Model Registry", "type": "item"}] | tojson)' | \
      kubectl apply -f - -n kubeflow
    echo "Waiting for the dashboard..."
    kubectl wait --for=condition=Ready pod -l 'app.kubernetes.io/name=centraldashboard' --timeout=180s -n kubeflow

    echo "Waiting for KFP..."
    kubectl wait --for=condition=Ready pod -l 'app.kubernetes.io/name=kubeflow-pipelines' --timeout=180s -n kubeflow

    echo ""
    echo "🎉 Installation complete! 🎉"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Run this command to start port forwarding:"
    echo "      kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80"
    echo ""
    echo "   2. Open your browser and go to:"
    echo "      http://localhost:8080"
    echo ""
    echo "   3. Login with these credentials:"
    echo "      Username: user@example.com"
    echo "      Password: 12341234"
    echo ""
```

**Note:** This script assumes `kustomize` and `jq` are installed and in your PATH. Ensure you have followed the prerequisites section to install these tools. Also, ensure you have cloned the `kubeflow/manifests` repository to `~/kubeflow-manifests-repo` and are running this script from that directory.






**Accessing the cluster:**
 After this complex setup, you would typically access the Kubeflow Central Dashboard via an Ingress or LoadBalancer, as described in the [Connect to your Kubeflow cluster](https://github.com/kubeflow/manifests?tab=readme-ov-file#connect-to-your-kubeflow-cluster) section of the `kubeflow/manifests` README.

***Once the full multi-user Kubeflow is deployed, you would then apply the Model Registry UI's Istio-dependent overlay:***
```
cd ~/kubeflow-manifests-repo/applications/model-registry/upstream/options/ui/overlays/istio
kubectl apply -k . -n kubeflow
```


This would then work because Istio would be present.

- Integrate Model Registry UI with Kubeflow Central Dashboard (Optional but Recommended): This step adds a direct link to the Model Registry UI in the Kubeflow Central Dashboard's navigation menu.
```
kubectl get configmap centraldashboard-config -n kubeflow -o json | \
jq '.data.links |= (fromjson | .menuLinks += [{"icon": "assignment", "link": "/model-registry/", "text": "Model Registry", "type": "item"}] | tojson)' | \
kubectl apply -f - -n kubeflow
```

***Note: This command requires jq to be installed (sudo dnf install jq). If you prefer, you can edit the ConfigMap manually: kubectl edit configmap -n kubeflow centraldashboard-config and add the menu item under data.links.menuLinks.***

**Set Up Port-Forwards:** 

Open three separate terminal windows and run:

- KFP UI: `kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80`
- Model Registry API: `kubectl port-forward -n kubeflow svc/model-registry-service 8082:8080`
- Model Registry UI: `kubectl port-forward -n kubeflow svc/model-registry-ui-service 8084:80`
- Minio (for KFP logs): `kubectl; port-forward -n kubeflow svc/minio-service 9000:9000`

# Connecting KFP to Model Registry: Best Practices

To enable your KFP component to register models, you need to provide it with the Model Registry's API endpoint and, ideally, an authentication token. While the Model Registry API can be accessed directly, using a Kubernetes Secret for sensitive information like tokens is a best practice.


**Create a Kubernetes Secret for the Model Registry Token:**

For local development, you might use a dummy token. For production, you'd generate a secure one.

`kubectl create secret generic model-registry-auth --from-literal=token='your-dummy-token' -n kubeflow`


***Note: In a real-world scenario, you would ensure the `pipeline-runner` ServiceAccount (or the ServiceAccount used by your pipeline) has permissions to read this Secret and that the Secret is mounted as an environment variable into your component's pod. This is often handled by a higher-level Kubeflow deployment or by manually patching the ServiceAccount/Deployment if needed.***

# Building the KFP Pipeline for Model Registration

### The `register_model_to_kubeflow_registry` Component

Our pipeline consists of a single custom component, `register_model_to_kubeflow_registry`, defined using KFP's `@dsl.component` decorator. This component encapsulates the logic for interacting with the Model Registry API.

* **Base Image & Dependencies:** The component uses a `python:3.11-slim-buster` base image, and the `model-registry==0.2.19` client library is automatically installed into its container environment via the `packages_to_install` argument in the decorator.
* **Model Registry Connection:** Inside the component, the `ModelRegistry` client is initialized. It connects to the Model Registry API server using its internal Kubernetes DNS name (`http://model-registry-service.kubeflow.svc.cluster.local:8080`).
* **Authentication:** For authentication, the component retrieves a token from the `MR_AUTH_TOKEN` environment variable using `os.environ.get()`. This environment variable is populated by mounting a Kubernetes Secret (`model-registry-auth`) into the component's pod, ensuring sensitive credentials are not hardcoded.
* **Dynamic Metadata for Lineage:** To achieve robust cross-referencing and lineage tracking, the component dynamically captures details about its own pipeline run. It retrieves values like `KFP_RUN_ID`, `KFP_PIPELINE_NAME`, and `KFP_POD_NAMESPACE` from environment variables that Kubeflow Pipelines automatically inject into every component pod. These values are then passed as `model_source_id`, `model_source_name`, `model_source_class`, `model_source_kind`, and `model_source_group` when registering the model.
* **Model Registration:** The core action involves calling `registry.register_model()`. This single call registers both the conceptual model and its specific version, requiring parameters such as `name`, `uri` (the model's artifact location), `description`, `model_format_name`, `model_format_version`, and the `version` string itself.
* **KFP Output Model Metadata:** To further enhance traceability within the KFP UI, the component writes a dummy model artifact to its `output_model` path. More importantly, it populates this `output_model`'s metadata with key information about the registered model, including its `modelName`, `versionName`, `modelID`, and a constructed `modelRegistryURL`. This metadata will be visible in the KFP UI's "Artifacts" tab for the pipeline run.

### The `model_registration_pipeline` Definition

The `model_registration_pipeline` orchestrates the `register_model_to_kubeflow_registry` component. This pipeline defines input parameters for the model's name, version, artifact URI, and author, allowing for flexible configuration when launching a run. It then invokes the component, passing these parameters. The pipeline is designed to return the registered model's ID as an output.

### Compiling and Deploying the Pipeline

Once defined in Python, the pipeline needs to be compiled into a YAML file, which is the format Kubeflow Pipelines understands. The `kfp.compiler.Compiler().compile()` function handles this, generating a `model_registration_pipeline.yaml` file. This YAML file can then be uploaded to the Kubeflow Pipelines UI and executed.




***Now, let's define a sample KFP pipeline that registers a fake model. This pipeline demonstrates best practices for setting `model_source` metadata, which is crucial for tracing model lineage back to its originating pipeline run.***

We'll use placeholders from `kfp.dsl` and `os.environ` to dynamically inject values like the pipeline run ID and name.

**The complete pipeline code is available on this [GitHub](https://github.com/hpurdom/blog/blob/master/code_examples/model_registration_pipeline_example.py) link here.**
