---
title: "🚀 Announcing the Kubeflow Spark Operator Benchmarking Results"
layout: post
toc: false
comments: true
image: 
hide: false
categories: [operators, benchmarking, performance]
permalink: 
author: "<a href='https://www.linkedin.com/in/varaprofile/'>Vara Bonthu</a>, <a href='https://www.linkedin.com/in/manabumccloskey/'>Manabu McCloskey</a>, <a href='https://www.linkedin.com/in/ratnopamc/'>Ratnopam Chakrabarti </a>, <a href='https://www.linkedin.com/in/alanhalcyon/'>Alan Halcyon</a>"
---

Kubernetes has become the go-to platform for running large-scale [Apache Spark](https://spark.apache.org/) workloads. But as workloads scale, **how do you ensure your Spark jobs run efficiently without hitting bottlenecks?** Managing thousands of concurrent Spark jobs can introduce **severe performance challenges**—from **CPU saturation** in the Spark Operator to **Kubernetes API slowdowns** and **job scheduling inefficiencies**.  

To address these challenges, we are excited to introduce the **Kubeflow Spark Operator Benchmarking Results and Toolkit**—a comprehensive framework to analyze performance, pinpoint bottlenecks, and optimize your Spark on Kubernetes deployments.

## 🔍 What's Included?
This benchmarking effort provides **three key outcomes** to help you take full control of your Spark on Kubernetes deployment:  

✅ **[Benchmarking Results](https://www.kubeflow.org/docs/components/spark-operator/performance/benchmarking/)** – A detailed evaluation of performance insights and tuning recommendations for large-scale Spark workloads.  
🛠 **[Benchmarking Test Toolkit](https://github.com/awslabs/data-on-eks/tree/main/analytics/terraform/spark-k8s-operator/examples/benchmark/spark-operator-benchmark-kit)** – A fully reproducible test suite to help users evaluate their own Spark Operator performance and validate improvements.  
📊 **[Open-Sourced Grafana Dashboard](https://grafana.com/grafana/dashboards/23032-spark-operator-scale-test-dashboard/)** – A **battle-tested** visualization tool designed specifically to track large-scale Spark Operator deployments, providing real-time monitoring of job processing efficiency, API latencies, and system health.

## ❌ The Challenges: Why Benchmarking Matters  
Running **thousands of Spark jobs** on Kubernetes at scale uncovers several **performance roadblocks** that can **cripple efficiency** if left unresolved:

- **🚦 Spark Operator Becomes CPU-Bound**: When handling thousands of Spark jobs, the controller pod maxes out CPU resources, limiting job submission rates.  
- **🐢 High API Server Latency**: As workloads scale, Kubernetes API responsiveness degrades—job status updates slow down, affecting observability and scheduling efficiency.  
- **🕒 Webhook Overhead Slows Job Starts**: Using webhooks adds **~60 seconds** of extra latency per job, reducing throughput in high-concurrency environments.  
- **💥 Namespace Overload Causes Failures**: Running **6,000+ SparkApplications in a single namespace** resulted in **pod failures** due to excessive environment variables and service object overload.

💡 **So, how do you fix these issues and optimize your Spark Operator deployment?**  
That's where our **benchmarking results and toolkit** come in.  


## 🛠 Tuning Best Practices for Spark Operator  
Based on our benchmarking findings, we provide **clear, actionable recommendations** for improving Spark Operator performance at scale.  

If you're running **thousands of concurrent Spark jobs**, here’s what you need to do:

### **Deploy Multiple Spark Operator Instances**  
💡 **Why?** A single Spark Operator instance struggles to keep up with high job submission rates.  
✅ **Solution**: When a single Spark Operator instance struggles with high job submission rates, leading to CPU saturation and slower job launches, **deploying multiple instances can help**. Distribute the workload by assigning different namespaces to each instance. For example, one instance can manage `**20 namespaces** while another handles a separate set of **20 namespaces**. This prevents bottlenecks and ensures efficient Spark job execution.

### **Disable Webhooks for Faster Job Starts**  
💡 **Why?** Webhooks introduce `~60 seconds` of delay per job due to validation and mutation overhead, reducing throughput in large workloads.
✅ **Solution**: Instead of using **webhooks** for volume mounts, node selectors, or taints, define **Spark Pod Templates** directly within the Spark job definition—no additional files are needed. Disable webhooks by setting `webhook.enable=false` in the Helm chart.

### **Increase Controller Workers**  
💡 **Why?** By default, the operator runs with **10 controller workers**, but our benchmarks showed increasing this to **20 or 30 workers** improved job throughput.  
✅ **Solution**: Set `controller.workers=20` if your Operator pod runs on a `36-core` CPU or higher to enable faster parallel job execution. For larger workloads (e.g., 72+ cores), increase to 40+ workers for better parallel job execution.

### **Enable a Batch Scheduler (Volcano / YuniKorn)**  
💡 **Why?** Kubernetes’ default scheduler isn't optimized for batch workloads, leading to **inefficient job placements**.  
✅ **Solution**: Enable **Volcano** or **YuniKorn** (`batchScheduler.enable=true`) to optimize job scheduling. These schedulers provide **gang scheduling, queue management, and multi-tenant resource sharing**. Benchmarks show that **Apache YuniKorn** schedules jobs faster than the default Kubernetes scheduler.

### **Optimize API Server Scaling**  
💡 **Why?** API server latency spikes to **600ms+ under heavy load**, affecting Spark job responsiveness.  
✅ **Solution**: Scale API server replicas, allocate more CPU and memory, and optimize event handling. Ensure your **Kubernetes API server and etcd** auto-scale to handle bursty workloads efficiently. Monitor `kube-apiserver` metrics and scale `etcd` accordingly. If running thousands of Spark pods, consider **manually increasing control plane node sizes**.

### **Distribute Spark Jobs Across Multiple Namespaces**  
💡 **Why?** Running too many jobs in a single namespace causes **environment variable overflows**, leading to pod failures.  
✅ **Solution**: When too many pods are placed in a single namespace, operations like listing or modifying resources can generate large **API server** responses, increasing latency. For example, retrieving all pods may result in a substantial size in response, consuming significant server resources. Additionally, **etcd**, Kubernetes' key-value store, can become a bottleneck when handling frequent updates from a high number of pods in one namespace. Heavy read and write operations can strain etcd, causing increased latencies and potential timeouts. To improve performance and stability, it is recommended to **distribute workloads across multiple namespaces**. 

### **Monitor & Tune Using the Open-Source Grafana Dashboard**  
💡 **Why?** Observability is key to identifying performance bottlenecks.  
✅ **Solution**: Use our **[Spark Operator Scale Test Dashboard](https://grafana.com/grafana/dashboards/23032-spark-operator-scale-test-dashboard/)** to track job submission rates, API latencies, and CPU utilization in real time.

## 📖 Learn More & Get Started  
The **Kubeflow Spark Operator Benchmarking Results and Toolkit** provide an in-depth **performance playbook** for running Spark at scale on Kubernetes. Whether you're troubleshooting an existing deployment or planning for future growth, this toolkit arms you with **data-driven insights** and **best practices** for success.  

🚀 **Ready to optimize your Spark workloads?** Dive into the full results and toolkit below:  
📖 **[Kubeflow Spark Operator Benchmarks](https://www.kubeflow.org/docs/components/spark-operator/performance/benchmarking/)**
