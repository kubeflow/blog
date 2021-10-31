---
title: "Unified training operator release announcement"
layout: post
toc: true
comments: true
hide: false
categories: [release]
permalink: /unified-training-operator-1.3-release/
author: "Johnu George, Jiaxin Shan, Josh Bottum"
---

The Kubeflow Training Operator Working Group introduced several enhancements in the recent Kubeflow 1.4 release. The most significant was the introduction of the new unified [training operator](https://github.com/kubeflow/training-operator) that enables Kubernetes custom resources (CR) for many of the popular training frameworks: Tensorflow, Pytorch, MXNet and XGboost. In addition, the `tf-operator` repository has been renamed to `training-operator`.  

This single operator provides several valuable benefits: 

1. **Better resource utilisation** - For  releases prior to 1.4, each framework had a separate corresponding controller managing its distributed job. The unified training operator manages all distributed jobs across frameworks, which improves resource utilization and performance.
2. **Less maintenance overhead** - Unified training operator reduces the maintenance efforts in managing distributed jobs across the framework. By default, all supported schemas(TFJob, PyTorchJob, MXNetJob, XGBoostJob) are enabled. However, specific schemas can be enabled using the flag 'enable-scheme'. Setting this flag enables the user to enable the framework(s) that are necessary for the deployment environment.
3. **Easy adoption of new operators** - Common code is abstracted from all framework implementations, which makes it easy for adopting new operators with less code. The common infrastructure [code](https://github.com/kubeflow/common) can be reused for many of the new operator efforts. Reference: Paddle operator [proposal](https://github.com/kubeflow/community/pull/502), DGL operator [proposal](https://github.com/kubeflow/community/pull/512)
4. **Better developer experience** - Common features can be shared across frameworks without code duplication thereby, creating a developer friendly environment. For example, Prometheus Monitoring and Job Scheduling features are common, making them available to all frameworks without any extra code.

The unified training operator’s [manifests](https://github.com/kubeflow/manifests/tree/v1.4-branch/apps/training-operator/upstream) include an enhanced training operator, which manages custom resource definitions for TFJob, PyTorchJob, MXNet Job and  XGBoostJob. All individual operator repositories, including [pytorch-operator](https://github.com/kubeflow/pytorch-operator), [mxnet-operator](https://github.com/kubeflow/mxnet-operator), [xgboost-operator](https://github.com/kubeflow/xgboost-operator), will be archived soon. Please check out the latest [release](https://github.com/kubeflow/training-operator/releases/tag/v1.3.0) for more details and give it a try! 

## Release highlights

Kubeflow 1.4 release includes the following major changes to training. 

### Universal Training Operator changes

* Unified Training Operator for TF, PyTorch, MXNet, XGBoost [#1302](https://github.com/kubeflow/tf-operator/pull/1302) [#1295](https://github.com/kubeflow/tf-operator/pull/1295) [#1294](https://github.com/kubeflow/tf-operator/pull/1294) [#1293](https://github.com/kubeflow/tf-operator/pull/1293) [#1296](https://github.com/kubeflow/tf-operator/pull/1296)
* More common code refactoring for reusability [#1297](https://github.com/kubeflow/tf-operator/pull/1297)
* API code restructuring to consistent format [#1300](https://github.com/kubeflow/tf-operator/pull/1300)
* Prometheus counters for all frameworks [#1375](https://github.com/kubeflow/tf-operator/pull/1375)
* Python SDK for all frameworks [#1420](https://github.com/kubeflow/tf-operator/pull/1420)
* API doc for all frameworks [#1370](https://github.com/kubeflow/tf-operator/pull/1370)
* Restructuring of examples across all frameworks [#1373](https://github.com/kubeflow/tf-operator/pull/1373) [#1391](https://github.com/kubeflow/tf-operator/pull/1391)

### Common package updates

* Make training container port customizable to support profiling [#131](https://github.com/kubeflow/common/pull/131)
* Optimize the TTL setting of all Jobs [#137](https://github.com/kubeflow/common/pull/137)
* More appropriate use of expectation for Jobs [#139](https://github.com/kubeflow/common/pull/139)


### MPI Operator updates 

* Scalability improvements to reduce pressure on kube-apiserver [#360](https://github.com/kubeflow/mpi-operator/pull/360)
* V2beta1 MPIJob API [#366](https://github.com/kubeflow/mpi-operator/pull/366) [#378](https://github.com/kubeflow/mpi-operator/pull/378)
* Intel MPI Support [#389](https://github.com/kubeflow/mpi-operator/pull/389) [#403](https://github.com/kubeflow/mpi-operator/pull/403) [#417](https://github.com/kubeflow/mpi-operator/pull/417) [#425](https://github.com/kubeflow/mpi-operator/pull/425)

## MPI Operator roadmap

The MPI framework integration with the unified training operator is under development and is planned for delivery in the next release i.e. post 1.4. Currently, it needs to be separately installed using MPIJob [manifests](https://github.com/kubeflow/manifests/tree/v1.4-branch/apps/mpi-job/upstream).

## Acknowledgement

The unified training operator is the outcome of efforts from all existing Kubeflow training operators and aims to provide a unified and simplified experience for both users and developers. We'd like to thank everyone who has contributed to and maintained the original operators.

* PyTorch Operator: [list of contributors](https://github.com/kubeflow/pytorch-operator/graphs/contributors) and [maintainers](https://github.com/kubeflow/pytorch-operator/blob/master/OWNERS)
* MPI Operator: [list of contributors](https://github.com/kubeflow/mpi-operator/graphs/contributors) and [maintainers](https://github.com/kubeflow/mpi-operator/blob/master/OWNERS)
* XGBoost Operator: [list of contributors](https://github.com/kubeflow/xgboost-operator/graphs/contributors) and [maintainers](https://github.com/kubeflow/xgboost-operator/blob/master/OWNERS)
* MXNet Operator: [list of contributors](https://github.com/kubeflow/mxnet-operator/graphs/contributors) and [maintainers](https://github.com/kubeflow/mxnet-operator/blob/master/OWNERS)

## Join the WG-Training 

If you want to help, or are looking for issues to work on, feel free to check the resources below! 

Slack: [#wg-training](https://kubeflow.slack.com/archives/C018N3M6QKB)

Community: [wg-training](https://github.com/kubeflow/community/tree/master/wg-training)

Issues: https://github.com/kubeflow/training-operator/issues

