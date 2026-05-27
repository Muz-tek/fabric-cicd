# Fabric Workload Repo

This folder is the template for the Azure DevOps Fabric workload repository.

It owns:

- Fabric notebooks.
- Fabric data pipelines.
- Fabric item definitions.
- Semantic models and reports.
- Deployment-rule documentation for environment-specific bindings.
- The `fabric-cicd` Azure Pipeline.

Only the Dev Fabric workspace is connected to this repo. Test and Prod are promoted through the Fabric deployment pipeline controlled by Azure DevOps.
