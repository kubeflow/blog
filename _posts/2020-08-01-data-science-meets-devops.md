---
title: "Data Science Meets Devops: MLOps with Jupyter, Git, & Kubernetes"
description: "An end-to-end example of deploying a machine learning product using Jupyter, Papermill, Tekton, GitOps and Kubeflow."
layout: post
toc: true
comments: true
image: images/2020-08-01-data-science-meets-devops/fig2.ci-cd.png
hide: false
search_exclude: false
categories: [jupyter, mlops, tekton, gitops]
permalink: /mlops/
author: "<a href='https://www.linkedin.com/in/jeremy-lewi-600aaa8/'>Jeremy Lewi</a>, <a href='https://hamel.dev/'>Hamel Husain</a>"
---

## The Problem

[Kubeflow](https://www.kubeflow.org/) is a fast-growing open source project that makes it easy to deploy and manage machine learning on Kubernetes.  

Due to Kubeflow’s explosive popularity, we receive a large influx of GitHub issues that must be triaged androuted to the appropriate subject matter expert.  The below chart illustrates the number of new issues opened for the past year:


<img src="/images/2020-08-01-data-science-meets-devops/fig1.num-issues.png" width="" alt="Number of Kubeflow Issues" title="">
<figcaption><strong>Figure 1:</strong>Number of Kubeflow Issues</figcaption>

To keep up with this influx, we started investing in a Github App called [Issue Label Bot](https://github.com/marketplace/issue-label-bot) that used machine learning to auto label issues.  Our [first model](https://github.com/marketplace/issue-label-bot) was trained using a collection of popular public repositories on GitHub and only predicted generic labels.  Subsequently, we started using [Google AutoML](https://cloud.google.com/automl/docs) to train a Kubeflow specific model. The new model was able to predict Kubeflow specific labels with average precision of 72% and average recall of 50%. This significantly reduced the toil associated with issue management for Kubeflow maintainers. The table below
contains evaluation metrics for Kubeflow specific labels.


Label | Precision | Recall
-- | -- | --
area-api | 1.0 | 0.0
area-backend | 0.6 | 0.4
area-bootstrap | 0.3 | 0.1
area-build-release | 1.0 | 0.2
area-centraldashboard | 0.6 | 0.6
area-components | 0.5 | 0.3
area-docs | 0.8 | 0.7
area-engprod | 0.8 | 0.5
area-example-code_search | 1.0 | 1.0
area-front-end | 0.7 | 0.5
area-frontend | 0.7 | 0.4
area-inference | 0.9 | 0.5
area-istio | 1.0 | 0.3
area-jupyter | 0.9 | 0.7
area-katib | 0.8 | 1.0
area-kfctl | 0.8 | 0.7
area-kustomize | 0.3 | 0.1
area-operator | 0.8 | 0.7
area-pipelines | 0.7 | 0.4
area-samples | 0.5 | 0.5
area-sdk | 0.7 | 0.4
area-sdk-dsl | 0.6 | 0.4
area-sdk-dsl-compiler | 0.6 | 0.4
area-testing | 0.7 | 0.7
area-tfjob | 0.4 | 0.4
platform-aws | 0.8 | 0.5
platform-gcp | 0.8 | 0.6

<figcaption>Table 1: Evaluation metrics for various Kubeflow labels.</figcaption>

Given the rate at which new issues are arriving, retraining our model periodically became a priority. We believe continuously retraining and deploying our model to leverage this new data is critical to maintaining the efficacy of our models.  


## Our Solution

Our CI/CD solution is illustrated in [Figure 2](#fig2). We don’t explicitly create a directed acyclic graph (DAG)  to connect the steps in an ML workflow (e.g. preprocessing, training, validation, deployment, etc…). Rather, we use a set of independent controllers. Each controller declaratively describes the desired state of the world and takes  actions necessary to make the actual state of the world match. This independence makes it easy for us to use whatever tools make the most sense for each step. More specifically we use

*   Jupyter notebooks for developing models. 
*   GitOps for continuous integration and deployment. 
*   Kubernetes and managed cloud services for underlying infrastructure.  

<img id="fig2" src="/images/2020-08-01-data-science-meets-devops/fig2.ci-cd.png" width="" alt="alt_text" title="">
<figcaption><strong>Figure 2:</strong> illustrates how we do CI/CD. Our pipeline today consists of two independently operating controllers. We configure the Trainer (left hand side) by describing what models we want to exist; i.e. what it means for our models to be “fresh”.  The Trainer periodically checks whether the set of trained models are sufficiently fresh and if not trains a new model. We likewise configure the Deployer (right hand side) to define what it means for the deployed model to be in sync with the set of trained models. If the correct model is not deployed it will deploy a new model.</figcaption>

The first controller, the Trainer, (left hand side of Figure 2) is a controller which checks if our model needs to be retrained. At the moment, this controller retrains the model after a set time period. When the model becomes stale, the controller  executes a [notebook ](https://github.com/kubeflow/code-intelligence/blob/master/Label_Microservice/notebooks/automl.ipynb) programmatically using [papermill.](https://github.com/nteract/papermill)  This notebook fetches GitHub Issues data [from BigQuery](https://medium.com/google-cloud/analyzing-github-issues-and-comments-with-bigquery-c41410d3308) and launches an [AutoML](https://cloud.google.com/automl) job to train a model. 

AutoML allowed us to focus on infrastructure and engineering rather than spending too much time building and tuning models.  Furthermore, AutoML provides a competitive baseline for us to improve upon.  We may revisit these models in the future.

The second component, the Deployer, (right hand side of Figure 2) determines which model should be live and if needed, automatically opens a pull request to update our model. Once the pull request is merged [Anthos Config Mesh](https://cloud.google.com/anthos/config-management) automatically rolls it out to production.

## Further Details

### Background

Before diving into the details of our solution we want to provide some context around:

1. What reconcilers are and why we use them
2. What GitOps is and why we adopted this pattern

### Building Resilient Systems With Reconcilers

A reconciler is a control pattern that has proven to be immensely useful for building resilient systems. The reconcile pattern is [at the heart of how Kubernetes works](https://book.kubebuilder.io/cronjob-tutorial/controller-overview.html). Figure 3 illustrates how a reconciler works. A reconciler works by first observing the state of the world; e.g. what model is currently deployed. The reconciler then compares this against the desired state of the world and computes the diff; e.g the model with label “version=20200724” should be deployed, but the model currently deployed has label “version=20200700”. The reconciler then takes the action necessary to drive the world to the desired state; e.g. open a pull request to change the deployed model.


<img src="/images/2020-08-01-data-science-meets-devops/fig3.reconciler.png" width="" alt="Figure 3" title="Figure 3. Illustration of the reconciler pattern as applied by our deployer.">

Reconcilers have proven immensely useful for building resilient systems because a well implemented reconciler provides a high degree of confidence that no matter how a system is perturbed it will eventually return to the desired state.


### There Are No DAGs

The declarative nature of controllers means data can flow through a series of controllers  without needing to explicitly create a DAG. In lieu of a DAG, a series of data processing steps can instead be expressed as a set of desired states, as illustrated in Figure 4 below:


<img src="/images/2020-08-01-data-science-meets-devops/fig4.data-pipeline.png" width="" alt="alt_text" title="">

<figcaption><strong>Figure 4:</strong> illustrates how pipelines can emerge from independent controllers without explicitly encoding a DAG. Here we have two completely independent controllers. The first controller ensures that for every element a<sub>i</sub> there should be an element b<sub>i</sub>. The second controller ensures that for every element b<sub>i</sub> there should be an element c<sub>i</sub>.</figcaption>
 
This reconciler-based paradigm offers the following benefits over many traditional DAG-based workflows:

*   **Resilience against failures**:  the system continuously seeks to achieve and maintain the desired state.  This state refers to both infrastructure (via Kubernetes manifests) and computation to be performed.  This is important in machine learning workflows where infrastructure is often strongly coupled with code (i.e. GPUs, databases, etc).
*   **Increased autonomy of engineering teams:** each team is free to choose the tools and infrastructure that suit their needs.  The reconciler framework only requires a minimal amount of coupling between controllers while still allowing one to write expressive workflows.
*   **Battle tested patterns and tools**:  This reconciler based framework does not invent something new.  Kubernetes has a rich ecosystem that makes building controllers super simple. The popularity of Kubernetes
means there is a large and growing community familiar with this pattern and supporting tools.


### GitOps: Operation By Pull Request

GitOps, Figure 5, is a pattern for managing infrastructure. The core idea of GitOps is that source control (doesn’t have to be git) should be the source of truth for configuration files  describing your infrastructure. Controllers can then monitor source control and automatically update your infrastructure as your config changes. This means to make a change (or undo a change) you just open a pull request.


<img src="/images/2020-08-01-data-science-meets-devops/fig5.gitops.png" width="" alt="alt_text" title="">

<figcaption><strong>Figure 5:</strong> To push a new model for Label Bot we create a PR updating the config map storing the id of the Auto ML model we want to use. When the PR is merged, <a href="https://cloud.google.com/anthos-config-management/docs">Anthos Config Management(ACM</a>) automatically rolls out those changes to our GKE cluster. As a result, subsequent predictions are made using the new model. (Image courtesy of <a href="https://www.weave.works/blog/automate-kubernetes-with-gitops">Weaveworks</a>)</figcaption>

### Putting It Together: Reconciler + GitOps = CI/CD for ML

With that background out of the way, let’s dive into how we built CI/CD for ML by combining the Reconciler and GitOps patterns.

There were three problems we needed to solve

1. How do we compute the diff between the desired and actual state of the world?
2. How do we affect the changes needed to make the actual state match the desired state?
3. How do we build a control loop to continuously run 1 & 2?

#### Computing Diffs

To compute the diffs we just write lambdas that do exactly what we want. So in this case we wrote two lambas

1. The [first lambda](https://github.com/kubeflow/code-intelligence/blob/faeb65757214ac93259f417b81e9e2fedafaebda/Label_Microservice/go/cmd/automl/pkg/server/server.go#L109) determines whether we need to retrain based on the age of the most recent model
2. The [second lambda](https://github.com/kubeflow/code-intelligence/blob/faeb65757214ac93259f417b81e9e2fedafaebda/Label_Microservice/go/cmd/automl/pkg/server/server.go#L49) determines whether the model needs to be updated by comparing the most recently trained model to the model listed in a config map checked into source control.

We wrap these lambdas in a simple web server and deploy on Kubernetes. One reason we chose this approach is because we wanted to rely on Kubernetes’ [git-sync](https://github.com/kubernetes/git-sync) to mirror our repository to a pod volume. This makes our lambdas super simple because all the git management is taken care of by a side-car running [git-sync](https://github.com/kubernetes/git-sync).

#### Actuation

To apply the changes necessary, we use Tekton to glue together various CLIs that we use to perform the various steps.

To train our model we have a [Tekton task ](https://github.com/kubeflow/code-intelligence/blob/faeb65757214ac93259f417b81e9e2fedafaebda/tekton/tasks/run-notebook-task.yaml#L34)that


1. Runs our notebook using [papermill](https://github.com/nteract/papermill).
2. Converts the notebook to html using [nbconvert](https://nbconvert.readthedocs.io/en/latest/).
3. Uploads the ipynb and html files to GCS using [gsutil](https://cloud.google.com/storage/docs/gsutil)

To deploy our model we have a [Tekton task](https://github.com/kubeflow/code-intelligence/blob/faeb65757214ac93259f417b81e9e2fedafaebda/tekton/tasks/update-model-pr-task.yaml#L68) that


1. Uses kpt to update our configmap with the desired value
2. Runs git to push our changes to a branch
3. Uses a wrapper around the [GitHub CLI](https://github.com/cli/cli) (gh) to create a PR

We picked Tekton because the primary challenge we faced was sequentially running a series of CLIs in various containers. Tekton is perfect for this. Importantly, all the steps in a Tekton task run on the same pod which allows data to be shared between steps using a pod volume. 


#### The Control Loop

Finally, we needed to build a control loop that would periodically invoke our lambdas and launch our Tekton pipelines as needed. We used kubebuilder to create a [simple custom controller](https://github.com/kubeflow/code-intelligence/tree/master/Label_Microservice/go). Our controller’s reconcile loop will call our lambda to determines whether a sync is needed and if so with what parameters. If a sync is needed the controller fires off a Tekton pipeline to perform the actual update. An example of our custom resource is illustrated below


```yaml
apiVersion: automl.cloudai.kubeflow.org/v1alpha1
kind: ModelSync
metadata:
  name: modelsync-sample
  namespace: label-bot-prod
spec:
  failedPipelineRunsHistoryLimit: 10
  needsSyncUrl: http://labelbot-diff.label-bot-prod/needsSync
  parameters:
  - needsSyncName: name
    pipelineName: automl-model
  pipelineRunTemplate:
    spec:
      params:
      - name: automl-model
        value: notavlidmodel
      - name: branchName
        value: auto-update
      - name: fork
        value: git@github.com:kubeflow/code-intelligence.git
      - name: forkName
        value: fork
      pipelineRef:
        name: update-model-pr
      resources:
      - name: repo
        resourceSpec:
          params:
          - name: url
            value: https://github.com/kubeflow/code-intelligence.git
          - name: revision
            value: master
          type: git
      serviceAccountName: auto-update
  successfulPipelineRunsHistoryLimit: 10

```


The custom resource specifies the endpoint, **needsSyncUrl**, for the lambda that computes whether a sync is needed and a Tekton PipelineRun, **pipelineRunTemplate**, describing the pipeline run to create when a sync is needed. The controller takes cares of the details; e.g. ensuring only 1 pipeline per resource is running at a time, garbage collecting old runs, etc… All of the heavy lifting is taken care of for us by Kubernetes and kubebuilder.


## Build Your Own CI/CD pipelines

Our code base is a long way from being polished, easily reusable tooling. Nonetheless it is all public  and could be a useful starting point for trying to build your own pipelines. 

Here are some pointers to get you started

1. Use the Dockerfile to build your own [ModelSync controller](https://github.com/kubeflow/code-intelligence/blob/master/Label_Microservice/go/Dockerfile)
2. [Modify the kustomize package](https://github.com/kubeflow/code-intelligence/tree/master/Label_Microservice/go/config/default) to use your image and deploy the controller
3. Define one or more lambdas as needed for your use cases
    *   You can use our [Lambda server](https://github.com/kubeflow/code-intelligence/blob/master/Label_Microservice/go/cmd/automl/pkg/server/server.go) as an example
    *    We wrote ours in go but you can use any language and web framework you like (e.g. flask)
4. Define Tekton pipelines suitable for your use cases; our pipelines(linked below) might be a useful starting point
    *   [Notebook Tekton task ](https://github.com/kubeflow/code-intelligence/blob/master/tekton/tasks/run-notebook-task.yaml) - Run notebook with papermill and upload to GCS
    *   [PR Tekton Task](https://github.com/kubeflow/code-intelligence/blob/master/tekton/tasks/update-model-pr-task.yaml) - Tekton task to open GitHub PRs
5. Define ModelSync resources for your use case; you can refer to ours as an example
*   [ModelSync Deploy Spec](https://github.com/kubeflow/code-intelligence/blob/master/Label_Microservice/auto-update/prod/modelsync.yaml) - YAML to continuously deploy label bot
*   [ModelSync Train Spec](https://github.com/kubeflow/code-intelligence/blob/master/Label_Microservice/auto-update/prod/retrain-model.yaml) - YAML to continuously train our model

 
 If you’d like to see us clean it up and include it in a future Kubeflow release please chime in on issue [kubeflow/kubeflow#5167](https://github.com/kubeflow/kubeflow/issues/5167).


## What’s Next


### Lineage Tracking

Since we do not have an explicit DAG representing the sequence of steps in our CI/CD pipeline understanding the lineage of our models can be challenging. Fortunately, Kubeflow Metadata solves this by making it easy for each step to record information about what outputs it produced using what code and inputs. Kubeflow metadata can easily recover and plot the lineage graph. The figure below shows an example of the lineage graph from our [xgboost example](https://github.com/kubeflow/examples/blob/master/xgboost_synthetic/build-train-deploy.ipynb).


<img src="/images/2020-08-01-data-science-meets-devops/fig6.lineage.png" width="" alt="alt_text" title="">

<figcaption><strong>Figure 6:</strong> screenshot of the lineage tracking UI for our <a href="https://github.com/kubeflow/examples/blob/master/xgboost_synthetic/build-train-deploy.ipynb">xgboost example</a>)</figcaption>


Our plan is to have our controller automatically write lineage tracking information to the metadata server so we can easily understand the lineage of what’s in production.


## Conclusion

Building ML products is a team effort. In order to move a model from a proof of concept to a shipped product, data scientists and devops engineers need to collaborate. To foster this collaboration, we believe it is important to allow data scientists and devops engineers to use their preferred tools.    Concretely, we wanted to support the following tools for Data Scientists, Devops Engineers, and [SRE](https://en.wikipedia.org/wiki/Site_Reliability_Engineering)s:


*   Jupyter notebooks for developing models. 
*   GitOps for continuous integration and deployment. 
*   Kubernetes and managed cloud services for underlying infrastructure.  

To maximize each team’s autonomy and reduce dependencies on tools, our  CI/CD process follows a decentralized approach. Rather than explicitly define a DAG that connects the steps, our approach relies on a series of controllers that can be defined and administered independently. We think this maps naturally to enterprises where responsibilities might be split across teams; a data engineering team might be responsible for turning weblogs into features, a modeling team might be responsible for producing models from the features, and a deployments team might be responsible for rolling those models into production. 


## Further Reading

If you’d like to learn more about GitOps we suggest this [guide](https://www.weave.works/technologies/gitops/) from Weaveworks. 

To learn how to build your own Kubernetes controllers the [kubebuilder book](https://book.kubebuilder.io/) walks through an E2E example.
