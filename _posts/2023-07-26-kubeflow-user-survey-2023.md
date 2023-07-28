---
title: "Kubeflow User Survey 2023"
layout: post
toc: false
comments: true
image: images/logo.png
hide: false
categories: [community]
permalink: /kubeflow-user-survey-2023/
author: "Anna Jung, Johnu George, and Josh Bottum"
---

In April 2023, the Kubeflow user survey opened, gathering community feedback. The survey aimed to comprehend the
adoption of Kubeflow and collect input on the benefits, gaps, and requirements for machine learning use cases.

The survey consisted of 21 questions, including multiple-choice and freeform formats. It ran from April 11th to May 26th
and received 90 responses. The 2023 survey yielded more targeted and actionable freeform answers, which provided further
insights into users’ requirements and potential enhancements for Kubeflow. Furthermore, we received a significant amount
of positive feedback regarding the factors that contribute to the success of Kubeflow and its community. One survey
respondent expressed their appreciation, stating, *“I love that it helps teams do high-quality ML work while providing
flexibility. I love that it is open-source. I love that the community keeps working hard and making it better.”* Another
respondent highlighted their liking for Kubeflow due to *“the broad potential of some of the projects (like Pipelines
components) and the different integrations that make for more of an end-to-end experience.”*

We thank everyone for participating in the survey and we will use both the improvements and positive feedback to steer
our efforts in enhancing Kubeflow, ensuring it remains a user-centric platform for all.

## Key Takeaways

- 84% of the users deploy more than one Kubeflow component
- The top 3 Kubeflow components are Pipelines (90%), Notebooks (76%), and Katib (47%)
- The top contrib component used by the user is KServe (62%)
- Documentation (55%) is the biggest gap in Kubeflow, followed by tutorials (50%) and tied for third place,
  installation (39%) and upgrades (39%)
- Monitoring models (45%) is the biggest gap in the users' ML lifecycle, followed by model registry (44%) and initial
  setup (39%)
- 52% of the users use the raw manifest installation to install Kubeflow
- The top distribution used to install Kubeflow is AWS (28%) followed by Google Cloud (17%)
- 74% of the users deploy Kubeflow on the cloud and 45% on-prem
- 49% of the users are running Kubeflow in production
- 17% of the users are contributing back to Kubeflow
- 49% of the users are keeping up with the latest Kubeflow 1.7 release and 43% are running a version behind Kubeflow 1.6

### Survey Respondents

![2023 survey demographics and location graph](/images/2023-07-26-kubeflow-user-survey-2023/demographics_location_industry.png)

The Kubeflow user survey drew responses from 90 members of the community mostly made up of members from the United
States (43%), Europe (34%), and Asia-Pacific (10%). The majority of the respondents were from the Tech industry (49%),
followed by Finance (13%) and Consulting (11%).

While there is diversity in roles that make up the community, most of the community members had the title MLOps
Engineer (18%), ML Engineer (17%), and Architect (15%).

In the last year’s 2022 User Survey, we started to see an increase in the number of users adopting Kubeflow in their
production environment and actively contributing to the Kubeflow project as their expertise with the project grew. This
year, we see the trend continuing with the highest percentage of Kubeflow running in production (49%) and the highest
number of users contributing to the project (17%). As the adoption of Kubeflow continues to rise, this will have a
significant impact on the positive growth and development of the project.

![2023 survey demographics kubeflow experience graph](/images/2023-07-26-kubeflow-user-survey-2023/demographics_kubeflow_experience.png)

### Documentation and Tutorials

![2023 survey Kubeflow gaps graph](/images/2023-07-26-kubeflow-user-survey-2023/kubeflow_gaps.png)

Documentation and tutorial have been a challenge in the community for a while, and the trend continues this year with
documentation (55%) voted as the number one biggest gap in Kubeflow, followed by Tutorials (49%) as the second biggest
gap.

In the previous surveys, the feedback on documentation and tutorials was very generic. However, this year, the users are
asking for specific documentation to help them adopt Kubeflow better. Some of the documentation and tutorials users are
looking for are the following:

- Tutorials and examples of how to leverage the new features delivered with the new releases
- An architecture diagram of Kubeflow of how each component works
- How to setup Transport Layer Security (TLS) with raw manifest installation
- A user onboarding documentation on how to add contributors to the platform and map credentials
- Documentation to show integration with other tools like MLflow
- Examples of all the capabilities of KFP packages
- Documentation to cover the RBAC and authorization in Kubeflow
- Upgrade guide for every release

In addition to the specific ask, the major themes in what type of documentation improvements users are asking for are

- Documentation for advanced users and advanced use cases
- Documentation for best practices around Kubeflow
- More diverse end-to-end examples, not just the mnist example
- Frequent updates to documentation as many are out of date

To address the challenges of Kubeflow documentation, we are looking for help from our community. If you are interested in
improving current Kubeflow documentation and work on future improvements, we invite you to join us at the next community
meeting to introduce yourself to the community.

### Installation and Upgrades

![2023 survey Kubeflow installation graph](/images/2023-07-26-kubeflow-user-survey-2023/kubeflow_installation.png)

One of the top three voted answers to the biggest gap in Kubeflow was installation tied with upgrades. The survey result
showed that 52% of the users use the raw manifest installation to install Kubeflow. With the sole support of Kustomize
as a choice of installation tool for Kubeflow, many users are looking for more diverse support for tooling, especially
Helm.

One of the biggest reasons for Helm support requests is due to complexity of installation. One survey respondent shared,
*“Kustomize does not quite provide the same experience and requires a lot more familiarity with the underlying systems
and manifests to properly configure…,”* which makes installation too difficult for a small team trying to adopt
Kubeflow.

For some, support for a different installation tool isn’t the answer. We also received much feedback on the installation
needing to be more lightweight. Due to the complexity of the stack and integration of many components, people are
struggling to customize their Kubeflow instance due to tight coupling and requirements of large resources.

In addition to installation, upgrades are also on top of the mind for many of the users. While there are some upgrade
guides for specific distributions, many of the users are installing Kubeflow without distribution. Without upgrade
guides provided for the raw manifest installation, upgrades are taking a great amount of effort for the users.

### Monitoring Models and Model Registry

![2023 survey Kubeflow ML lifecycle gaps graph](/images/2023-07-26-kubeflow-user-survey-2023/kubeflow_gaps_ml_lifecycle.png)

In last year’s survey, monitoring surged to the top as the biggest gap in the machine learning lifecycle. This year, the
trend continued with monitoring (45%) voted as the number one concern, closely followed by model registry (44%).

For both gaps, users are looking for a built-in solution that addresses monitoring and model registry needs, with
specific requests for support of Grafana and MLflow integrations to enable a seamless experience with Kubeflow
pipelines. With a lack of support for both of these tools, users are expressing concerns about the challenges they face
in managing and tracking their models.

### Security

In the previous [2022 Kubeflow User Survey](https://blog.kubeflow.org/kubeflow-user-survey-2022/), security emerged as
one of the top three voted answers, highlighting it as a significant gap in Kubeflow. Since then, the community has
placed a strong emphasis on security, leading to the formation of the Kubeflow Security Team comprising members with a
security-focused mindset. Their primary objective is to address security concerns and ensure that Kubeflow remains a
robust and secure platform for all its users. For further details, visit
the [Kubeflow security team](https://github.com/kubeflow/kubeflow/tree/master/security) and consider joining the next
security team meeting.

## What’s Next?

Currently, all working groups are working towards the 1.8 release, planned to release
on [October 4th, 2023](https://github.com/kubeflow/community/tree/master/releases/release-1.8). Upon successful delivery
of the 1.8 release, each working group will shift their focus towards prioritizing features for the next subsequent
release. During the initial planning phase of the new release, each working group leads will reevaluate the survey
results to determine their priorities driven by your survey feedback. If you are interested in the future direction of
each working group, join them in discussing their roadmap at their future meetings. All Kubeflow community meetings can
be found in
the [Kubeflow community calendar](https://www.kubeflow.org/docs/about/community/#kubeflow-community-calendars).

As for improvements to the documentation and tutorials, Kubeflow community is actively seeking help from our community
members. If you are interested in improving current Kubeflow documentation and work on future improvements, we invite
you to join us at the next community meeting to introduce yourself to the community and express your interest in joining this effort.

## Join the Community

We would like to thank everyone for their participation in the survey. As you can see from the survey results, the
Kubeflow Community is vibrant and diverse, solving real-world problems for organizations worldwide.

Want to help? The Kubeflow Community Working Groups hold open meetings and are always looking for more volunteers and
users to unlock the potential of machine learning. If you’re interested in becoming a Kubeflow contributor, check out
the [Kubeflow community page](https://www.kubeflow.org/docs/about/community/) to learn more. We look forward to working with you!
