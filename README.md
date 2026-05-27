# fabric-cicd

Microsoft Fabric CI/CD platform scaffold for Azure DevOps.

The implementation target is:

- A Fabric workload Azure Repos repository for notebooks, data pipelines, semantic models, reports, and item definitions.
- A platform/IaC Azure Repos repository for Terraform, Azure Pipelines YAML, scripts, documentation, and runbooks.
- Azure Pipelines for CI, release, approvals, and Dev to Test to Prod promotion.
- Terraform for Fabric workspace setup, Dev workspace Git integration, Fabric deployment pipeline setup, Azure operational resources, and Azure DevOps pipeline definitions.

Start with [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md).
