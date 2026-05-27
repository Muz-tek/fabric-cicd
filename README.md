# fabric-cicd

Microsoft Fabric CI/CD platform scaffold for Azure DevOps.

This repo is organized as two Azure DevOps repo templates:

- `iac/`: platform/IaC repo template with Terraform and the `iac-platform` Azure Pipeline.
- `fabric/`: Fabric workload repo template with notebooks/pipelines/items folders and the `fabric-cicd` Azure Pipeline.

The pipelines are deliberately separate:

- IaC changes plan/apply platform resources only.
- Fabric workload changes validate Fabric assets, sync Dev from Git, then promote Dev to Test to Prod through Fabric deployment pipelines.

Start with [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md).
