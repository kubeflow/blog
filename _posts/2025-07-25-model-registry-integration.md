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




Introduction: Centralizing Your ML Models with Kubeflow



In the journey of Machine Learning Operations (MLOps), managing trained models effectively is as crucial as building them. While Kubeflow Pipelines (KFP) provides powerful orchestration for your ML workflows, the Kubeflow Model Registry steps in as the centralized hub for versioning, cataloging, and discovering your machine learning models.




This blog post will serve as a practical guide, walking you through the process of integrating the Kubeflow Model Registry directly into your KFP pipelines. We'll cover the benefits, best practices for model registration, and provide a hands-on example, drawing from real-world troubleshooting steps encountered during setup on a local kind cluster.



Why Leverage Model Registry in Your Pipelines?

Integrating model registration as a native step within your Kubeflow Pipelines offers significant advantages for robust MLOps:

Centralized Cataloging: Move beyond scattered model files. The Model Registry provides a single source of truth for all your models, making them easily discoverable across your organization.

Structured Versioning & Lineage: Automatically track different iterations of your models. Each model version can be linked back to the exact pipeline run that produced it, ensuring full traceability and reproducibility.

Enhanced Governance & Auditability: Maintain a clear record of model lifecycles, crucial for compliance and auditing.

Seamless Handover to Serving: Registered models can be easily referenced by model serving platforms like KServe (formerly KFServing), streamlining deployment and management.

Automated Workflow: Eliminate manual steps. Once a model passes evaluation within a pipeline, it can be automatically registered, reducing human error and accelerating deployment.



You'd typically want to register a model from a pipeline when it has met predefined performance criteria, passed validation, and is ready to be shared, deployed, or archived.
Models vs. Model Versions: A Key Distinction
Understanding the core entities in the Model Registry is fundamental:
Registered Model: This represents the conceptual model. Think of it as a logical grouping for all iterations of a particular ML solution (e.g., "Fraud Detection Classifier," "Customer Churn Predictor").
Model Version: This is a specific iteration or snapshot of a Registered Model. Each version is immutable and holds unique artifacts, metadata, and a precise lineage (e.g., "v1.0.0," "v1.0.1-retrained," "v2025-07-18-production").
Getting Started: Setting Up Your Local Kubeflow Environment
To follow this guide, you'll need a local Kubernetes cluster with Kubeflow Pipelines and the Kubeflow Model Registry deployed. We'll use kind (Kubernetes in Docker) for this setup.
Prerequisites
A container engine (e.g., Docker).
Python (3.11 or newer).
kubectl: Kubernetes command-line tool.
kind: Kubernetes in Docker.
helm: Kubernetes package manager.
git: For cloning repositories.
Common Troubleshooting during Setup:
Setting up complex MLOps tools locally can be challenging. Here, we provide the robust deployment steps, incorporating solutions for common issues encountered during this process:
kind Cluster Instability / DNS Issues (ImagePullBackOff, Temporary failure in name resolution, nf_conntrack_ipv4 not found): These often stem from conflicts with your host's Docker networking, VPNs, or missing kernel modules.
Solution: Aggressive Docker/kind cleanup (sudo docker system prune -a --volumes -f), ensuring kind is installed correctly (refer to kind's installation guide), and a full system logout/login to refresh the environment.
KFP Core Component Crashes (metadata-grpc-deployment CrashLoopBackOff with Exit Code 139 - Segmentation Fault): This often indicates an incompatibility between the ml_metadata_store_server image and your host's kernel.
Solution: Patch the local KFP manifests to use an older, more compatible image version (e.g., 1.13.0 or 1.12.0) in ~/kfp-local-manifests/manifests/kustomize/base/metadata/base/metadata-grpc-deployment.yaml.
PersistentVolumeClaim (PVC) Pending: This means the cluster's local storage provisioner isn't working.
Solution: A full kind and Docker reset (sudo systemctl stop docker, sudo systemctl start docker) often resolves this by restarting the kind's default local path provisioner.
"Pipeline version creation failed" / "Cannot find context" in KFP UI: These are symptoms of KFP's core components (especially ML Metadata and the KFP API server) not being fully Running and READY.
Solution: Patience and verifying kubectl get pods -n kubeflow are key.
Model Registry Pods Missing / CreateContainerConfigError: This usually indicates a configuration problem preventing the container from starting. While transient network issues can sometimes cause similar symptoms, for CreateContainerConfigError, a manifest fix is often needed. If persistent, ensure your Model Registry deployment manifests (e.g., from your cloned repository) are up-to-date, as an outdated fork might lead to incompatibilities with other Kubeflow components. We found success deploying the Model Registry using its Kustomize manifests from the kubeflow/model-registry repository's overlays/db directory.
model_registry.exceptions.StoreError: Version X already exists: This error occurs when you try to register a model version with a model_name and model_version_name combination that already exists in the Model Registry.
Solution: This indicates the Model Registry is working as intended! Simply provide a new, unique model_version_name for your pipeline run (e.g., v1.0.1, v2.0.0, or v1.0.0-run-timestamp).
Deployment Steps:
Install kind (if not already installed via dnf):
sudo dnf install kind # Recommended for Fedora
# OR manual install if dnf fails (e.g., if 'No match for argument: kind'):
# cd ~
# curl -Lo kind https://kind.sigs.k8s.io/dl/v0.22.0/kind-linux-amd64
# chmod +x kind
# sudo mv kind /usr/local/bin/kind
# Perform a full system logout and login after any kind installation/update.

Clone Kubeflow Pipelines Repository:

cd ~
git clone https://github.com/kubeflow/pipelines.git kfp-local-manifests



If you needed to patch metadata-grpc-deployment.yaml for image compatibility (e.g., changing ml_metadata_store_server:1.14.0 to 1.13.0 for Exit Code 139 fix), do it now in ~/kfp-local-manifests/manifests/kustomize/base/metadata/base/metadata-grpc-deployment.yaml.
Deploy Kubeflow Pipelines on kind (Recommended Method): This make target automates the kind cluster creation and KFP deployment using the platform-agnostic manifests.

cd ~/kfp-local-manifests/backend # Navigate to the backend directory
make kind-cluster-agnostic



Note: This command will create the kind cluster (if it doesn't exist), deploy all necessary KFP components, and wait for core deployments (MySQL, MLMD, KFP API) to become available. This process can take 10-20 minutes or more. Monitor its output carefully.
Troubleshooting make kind-cluster-agnostic: If you encounter "No rule to make target" or other errors, ensure your kubeflow/pipelines repository clone is up-to-date and contains this target in backend/Makefile.
Verify KFP Health:
After make kind-cluster-agnostic finishes, open a new terminal.
Run this command repeatedly until ALL (or almost all) pods in the kubeflow namespace are Running and READY (1/1 or X/Y where X=Y).

kubectl get pods -n kubeflow

This is crucial. Do not proceed until KFP is healthy.
Clone Kubeflow Model Registry Repository:

cd ~
git clone https://github.com/kubeflow/model-registry.git

Deploy Kubeflow Model Registry (API Server): This deploys the Model Registry API server, which stores and serves model metadata.

cd ~/model-registry/manifests/kustomize/overlays/db # Navigate to the correct overlay for embedded DB
kubectl apply -k . -n kubeflow



Troubleshooting Model Registry Pods: Wait for model-registry-deployment pod to become Running and READY (kubectl get pods -n kubeflow | grep model-registry).
Install and Deploy Kubeflow Model Registry UI: The Model Registry UI is a separate frontend application that provides a browsable interface to your registered models. There are two primary ways to deploy it: a simpler method for basic setups, and a more comprehensive method for multi-user Kubeflow environments.
Option A: Basic UI Deployment (Recommended for simplicity with standalone KFP): This method deploys the UI without requiring Istio or other multi-user components.
Installation (Cloning the kubeflow/manifests repository, pinned to a compatible release): First, clone the Kubeflow manifests repository (if you haven't already). We recommend pinning to a specific release (e.g., v1.7.0) compatible with KFP 2.5.0.

cd ~
git clone https://github.com/kubeflow/manifests.git kubeflow-manifests-repo # Clone to a distinct name
cd kubeflow-manifests-repo
git fetch --tags
git checkout tags/v1.7.0 # Pin to Kubeflow manifests v1.7.0 (compatible with KFP 2.5.0)

Deployment (Applying manifests): Navigate to the Model Registry UI base overlay:

cd ~/kubeflow-manifests-repo/applications/model-registry/upstream/options/ui/base # Using 'base' overlay for non-Istio



Apply the UI manifests:

kubectl apply -k . -n kubeflow

Wait for the UI pod to be ready:

kubectl get pods -n kubeflow -l app=model-registry-ui

Option B: Multi-User Kubeflow Deployment (More comprehensive, but complex): This option deploys a full multi-user Kubeflow environment, which includes Istio, Dex, and other components necessary for authentication and traffic management. This path is significantly more time-consuming and complex to set up, but it enables the Model Registry UI to integrate with the Central Dashboard in a production-like, authenticated manner.
Note: This is a major deployment effort that goes beyond the scope of a simple Model Registry integration. It involves deploying many components from the root of the kubeflow/manifests repository. The exact steps are detailed in the Kubeflow manifests README under the "Deploy Kubeflow in Multi-User Mode" section.
Steps (summary from kubeflow/manifests README):
Create the Kind cluster (if not already done).
Install cert-manager.
Install Istio.
Install Oauth2-proxy.
Install Dex (skip identity provider connection for basic setup).
Deploy Kubeflow Namespace, Roles, and Istio Resources.
Install Kubeflow Pipelines (full version).
Install Central Dashboard.
Configure Profiles + KFAM (Kubeflow Access Management).
Configure User Namespaces.
Accessing the cluster: After this complex setup, you would typically access the Kubeflow Central Dashboard via an Ingress or LoadBalancer, as described in the Connect to your Kubeflow cluster section of the kubeflow/manifests README.
Once the full multi-user Kubeflow is deployed, you would then apply the Model Registry UI's Istio-dependent overlay:

cd ~/kubeflow-manifests-repo/applications/model-registry/upstream/options/ui/overlays/istio
kubectl apply -k . -n kubeflow



This would then work because Istio would be present.
Integrate Model Registry UI with Kubeflow Central Dashboard (Optional but Recommended): This step adds a direct link to the Model Registry UI in the Kubeflow Central Dashboard's navigation menu.

kubectl get configmap centraldashboard-config -n kubeflow -o json | \
jq '.data.links |= (fromjson | .menuLinks += [{"icon": "assignment", "link": "/model-registry/", "text": "Model Registry", "type": "item"}] | tojson)' | \
kubectl apply -f - -n kubeflow



Note: This command requires jq to be installed (sudo dnf install jq). If you prefer, you can edit the ConfigMap manually: kubectl edit configmap -n kubeflow centraldashboard-config and add the menu item under data.links.menuLinks.
Set Up Port-Forwards: Open three separate terminal windows and run:
KFP UI: kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
Model Registry API: kubectl port-forward -n kubeflow svc/model-registry-service 8082:8080
Model Registry UI: kubectl port-forward -n kubeflow svc/model-registry-ui-service 8084:80
Connecting KFP to Model Registry: Best Practices
To enable your KFP component to register models, you need to provide it with the Model Registry's API endpoint and, ideally, an authentication token. While the Model Registry API can be accessed directly, using a Kubernetes Secret for sensitive information like tokens is a best practice.
Create a Kubernetes Secret for the Model Registry Token: For local development, you might use a dummy token. For production, you'd generate a secure one.

kubectl create secret generic model-registry-auth --from-literal=token='your-dummy-token' -n kubeflow



Note: In a real-world scenario, you would ensure the pipeline-runner ServiceAccount (or the ServiceAccount used by your pipeline) has permissions to read this Secret and that the Secret is mounted as an environment variable into your component's pod. This is often handled by a higher-level Kubeflow deployment or by manually patching the ServiceAccount/Deployment if needed.
Building the KFP Pipeline for Model Registration
Now, let's define a sample KFP pipeline that registers a fake model. This pipeline demonstrates best practices for setting model_source metadata, which is crucial for tracing model lineage back to its originating pipeline run.
We'll use placeholders from kfp.dsl and os.environ to dynamically inject values like the pipeline run ID and name.


