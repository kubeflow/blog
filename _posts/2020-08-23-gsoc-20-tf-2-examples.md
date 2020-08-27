---
title: "GSoC '20: Notebook to Kubeflow Samples with TF 2.0 Keras"
description: "An important milestone in my journey of open source"
layout: post
toc: true
comments: true
hide: false
search_exclude: false
image: /images/2020-08-23-gsoc-20-tf-2-examples/logos.jpg
categories: [gsoc, examples, jupyter]
author: "<a href='https://www.linkedin.com/in/yash-jakhotiya/'>Yash Jakhotiya</a>"
---

# Introduction

Open source software development and [Google Summer of Code](https://summerofcode.withgoogle.com/), both started long before the summer of 2020. When the world was starting to grapple with the realities of [remote work](https://www.entrepreneur.com/article/354872), open source community was already thriving on it. Over the course of my college years, I have found out three things that I am passionate about - open source, machine learning and [SRE](https://landing.google.com/sre/). [Kubeflow](https://www.kubeflow.org/) has managed to incorporate all of these into one and doing a project with this organisation has been a dream come true!

# Aim

[Kubernetes](https://kubernetes.io/) is already an industry-standard in managing cloud resources. Kubeflow is on its path to become an industry standard in managing machine learning workflows on cloud. Examples that illustrate Kubeflow functionalities using latest industry technologies make Kubeflow easier to use and more accessible to all potential users. This project has aimed at building samples for Jupyter notebook to Kubeflow deployment using Tensorflow 2.0 Keras for backend training code, illustrating customer user journey (CUJ) in the process. This project has also served as an hands-on to large scale application of machine learning bringing in the elements of DevOps and SRE and this has kept me motivated throughout the project.

# The Kubeflow Community

The [Kubeflow community](https://www.kubeflow.org/docs/about/community/) is a highly approachable and closely-knit community that has been reaching out to and [helping](https://www.kubeflow.org/docs/about/gsoc/) potential GSoC students well before the application period. Respecting this, I made sure to take feedback for my proposal of the [project idea](https://summerofcode.withgoogle.com/projects/#5507335985823744) I chose, before the application deadline. Mentors [Yuan Tang](https://github.com/terrytangyuan), [Ce Gao](https://github.com/gaocegege) and [Jack Lin](https://github.com/ChanYiLin) were candid in providing me feedback and I refined and changed my proposal accordingly. To my sweet surprise, I got selected for the idea!😁 What has really helped me in these three months of coding period is that one month of [community bonding](https://developers.google.com/open-source/gsoc/timeline) where I got to know the community and more about the technicalities of Kubeflow.

# The Project

Examples created as part of this project needed to be easily reproducible to serve their purpose. Initially the underlying model decided to demonstrate Kubeflow functionalities was a BiDirectional RNN to be trained on IMDB large movie review [dataset](http://ai.stanford.edu/%7Eamaas/data/sentiment/) for sentiment analysis based on a [tensorflow tutorial](https://www.tensorflow.org/tutorials/text/text_classification_rnn). Over the course of time, we decided to also add another set of examples using  a neural machine translation model in its backend trained on a Spanish to English [dataset](http://www.manythings.org/anki/) based on another [tensorflow tutorial](https://www.tensorflow.org/tutorials/text/nmt_with_attention).

The reasons for choosing these models were -
* The [kubeflow/examples](https://github.com/kubeflow/examples) repo needed more NLP-related tasks.
* These were more of *hello world* tasks in the field of NLP. So that users who go through these samples need not worry about training code and focus more on Kubeflow's functionalities.
* These are based on tensorflow tutorials. Kubeflow tutorials based on Tensorflow tutorials show better coupling between the two.

## Repository Structure

I created a [repo](https://github.com/yashjakhotiya/kubeflow-gsoc-2020) under my own profile to regularly push commits to and my mentors consistently reviewed the work I pushed there. This repo has all of my work with the log history preserved. Each of the two models has following notebooks explaining core Kubeflow functionalities - 

1. `<training-model>.py` - This is the core training code upon which all subsequent examples showing Kubeflow functionalities are based. Please go through this first to know more about the machine learning task subsequent notebooks will manage.

2. `distributed_<training-model>.py` - To truly take advantage of multiple compute nodes, the training code has to be modified to support distributed training. The code in the above file is modified with Tensorflow's [distributed training](https://www.tensorflow.org/guide/distributed_training) strategy and hosted here.

3. `Dockerfile` - This is the dockerfile which is used to build Docker image of the training code. Some Kubeflow functionalities require that a docker image of the training code is built and hosted on a docker container registry. This Docker 101 [tutorial](https://www.docker.com/101-tutorial) is a good starting point to get hands-on training on Docker. For complete starters in the field of containerization, this [introduction](https://opensource.com/resources/what-docker) can serve as a good starting point.

4. `fairing-with-python-sdk.ipynb` - Fairing is a Kubeflow functionality that lets you run model training tasks remotely. This is the Jupyter notebook which deploys a model training task on cloud using Kubeflow Fairing. Fairing does not require you to build a Docker image of the training code first. Hence, its training code resides in the same notebook. To know more about Kubeflow Fairing, please visit Fairing's [official documentation](https://www.kubeflow.org/docs/fairing/fairing-overview/)

5. `katib-with-python-sdk.ipynb` - [Katib](https://www.kubeflow.org/docs/components/hyperparameter-tuning/hyperparameter/) is a Kubeflow functionality that lets you perform hyperparameter tuning experiments and reports best set of hyperparameters based ona provided metric. This is the Jupyter notebook which launches Katib hyperparameter tuning experiments using its [Python SDK](https://github.com/kubeflow/katib/tree/master/sdk/python). Katib requires you to build and host a Docker image of your training code in a container registry. For this sample, we have used [gcloud builds](https://cloud.google.com/cloud-build/docs) to build the required Docker image of the training code along with the training data and hosts it on [gcr.io](gcr.io).

6. `tfjob-with-python-sdk.ipynb` - [TFJobs](https://www.kubeflow.org/docs/components/training/tftraining/) are used to run distributed training jobs over Kubernetes. With multiple workers, TFJob truly leverage the ability of your code to support distributed training. This Jupyter notebook demonstrates how to use TFJob. The Docker image built from the distributed version of our core training code is used in this notebook.

7. `tekton-pipeline-with-python-sdk.ipynb` - [Kubeflow Pipeline](https://www.kubeflow.org/docs/pipelines/overview/pipelines-overview/) is a platform that lets you build, manage and deploy end-to-end machine learning workflows. This is a Jupyter notebook which bundles Katib hyperparameter tuning and TFJob distributed training into one Kubeflow pipeline. The pipeline used here uses [Tekton](https://cloud.google.com/tekton) in its backend. Tekton is a Kubernetes resource to create efficient [continuous integration and delivery](https://opensource.com/article/18/8/what-cicd) (CI/CD) systems.

## Final Merge PR

I copied these built notebooks and the final work product into a directory created in my fork of the [kubeflow/examples](https://github.com/kubeflow/examples) repo and created a [PR](https://github.com/kubeflow/examples/pull/816) to add these notebooks in Kubeflow's official repo. The PR got merged and the code currently resides in [kubeflow/examples/tensorflow_cuj](https://github.com/kubeflow/examples/tree/master/tensorflow_cuj) directory.

# Special Thanks

Special thanks are due to -
* My mentors for their valuable guidance throughout the project.
* [Jeremy](https://www.linkedin.com/in/jeremy-lewi-600aaa8/) and [Sarah](https://www.linkedin.com/in/sarahmaddox/?originalSubdomain=au) for smooth conduction of the Kubeflow GSoC program.
* The GSoC Discord [Server](https://discord.com/channels/708636399666069514/708636400097951744) and the GSoC Telegram [Channel](https://web.telegram.org/#/im?p=s1263176603_5411849872541551939) for the help, casual talks and a strong global student community.