---
 title: "Kubeflow's 1.4 release introduces the new unified training operator"
 layout: post
 toc: true
 comments: true
 hide: false
 categories: [release]
 permalink: /unified-training-operator-1.3-release/
 author: "Johnu George, Jiaxin Shan , Josh Bottum"
 ---

The Kubeflow 1.4 release introduced several enhancements to by the Training Operator Working Group, including a change of the repository name from tf-operator to training-operator. PR# 
In 1.4, the most significant delivery from the Training Operator Working Group was the delivery of the new unified training operator that enables Kubernetes custom resources (CR) for many of the popular training frameworks: Tensorflow, Pytorch, MXNet and XGboost.  This single operator provides several valuable benefits: 
1.	Better resource utilisation - For  releases prior to 1.4, each framework had a separate corresponding controller managing its  distributed job.  The unified training operator manages all distributed jobs across frameworks, which improves resource utilization and performance.
2. Less maintenance overhead - Unified training operator reduces the maintenance efforts in managing distributed jobs across the framework. By default, all supported schemas(TFJob, PyTorchJob, MXNetJob, XGBoostJob) are enabled.  However, specific schemas can be enabled using the flag 'enable-scheme'.   Setting this flag enables the user to enable the framework(s) that are necessary for the deployment environment.
3. Easy adoption of new operators - Common code is abstracted from all framework implementations, which makes it easy for adopting new operators with less code.  The common infrastructure code can be reused for many of the new operator efforts. Reference: Paddle operator proposal, DGL operator proposal
4. More developer friendly - Common features can be shared across frameworks without code duplication thereby, creating a developer friendly environment. Eg: Prometheus monitoring,  Job Scheduling features are common, making them available to all frameworks without any extra code.

The unified training operator’s manifests includes an enhanced training operator, which manages custom resource definitions for TFJob, PyTorchJob, MXNet Job and  XGBoostJob.  All individual operator repositories including pytorch-operator,  mxnet-operator,  xgboost-operator will be archived soon. Please check out the latest release for more details and give it a try! 

## More Details

Kubeflow 1.4 release has the following major changes
Universal Training Operator changes
Unified Training Operator for TF, PyTorch, MXNet, XGBoost #1302 #1295 #1294 #1293 #1296
More common code refactoring for reusability  #1297
API code restructuring to consistent format #1300
Prometheus counters for all frameworks #1375
Python SDK for all frameworks #1420
API doc for all frameworks #1370
Restructuring of examples across all frameworks #1373 #1391

## Common package changes

Make training container port customizable to support profiling #131
Optimize the TTL setting of all Jobs #137
More appropriate use of expectation for Jobs #139


## MPI-Operator updates

Scalability  improvements to reduce pressure on kube-apiserver #360
V2beta1 MPIJob API #366 #378 
Intel MPI Support #389 #403 #417 #425


## MPI current support and roadmap update

The MPI framework integration with the unified training operator is under development and is planned for delivery in the next release i.e. post 1.4.  Currently,  it needs to be separately installed using MPIJob manifests.

## Join the WG-Training 

If you want to help or are looking for issues to work on, feel free to check resources below! 

Slack: #wg-training
Community: https://github.com/kubeflow/community/tree/master/wg-training
Issues: https://github.com/kubeflow/training-operator/issues

