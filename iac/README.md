# Fabric Platform IaC Repo

This folder is the template for the Azure DevOps platform/IaC repository.

It owns:

- Terraform for Fabric workspaces, Dev workspace Git integration, deployment pipeline stages, roles, and operational Azure resources.
- The `iac-platform` Azure Pipeline.
- Platform runbooks and implementation documentation.

It does not deploy notebooks, Fabric data pipelines, reports, or semantic models. Those live in the Fabric workload repo.

Access is managed with Entra ID groups through Terraform where supported:

- Workspace Admins across Dev/Test/Prod.
- Data engineers and data scientists as Contributors in Dev/Test.
- Viewers in Prod.
- Deployment pipeline Admins.

Tenant, capacity, OneLake security, sensitivity labels, domains, and sharing/export policies are governed through Fabric admin processes and documented in `policies/fabric-access-and-governance.md`.
