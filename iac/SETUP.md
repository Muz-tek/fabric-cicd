# Platform/IaC Repo Setup

Copy the contents of this `iac/` folder into the Azure DevOps platform/IaC repository.

## Required Inputs

- Azure DevOps organization URL.
- Azure DevOps project name.
- Platform/IaC Azure Repos repository name.
- Fabric workload Azure Repos repository name.
- Azure Resource Manager service connection name.
- Fabric capacity ID.
- Fabric configured Git connection ID for the workload repo.
- Entra ID group object IDs for:
  - workspace admins
  - Dev/Test contributors
  - Prod viewers
  - deployment pipeline admins

## Bootstrap Steps

1. Create two Azure Repos repositories:
   - platform/IaC repo
   - Fabric workload repo
2. Copy the contents of `iac/` into the platform/IaC repo.
3. Copy the contents of `fabric/` into the Fabric workload repo.
4. Create or confirm the Azure Resource Manager service connection.
5. Ensure the service connection identity has the required Azure and Fabric permissions.
6. Enable required Fabric tenant settings for Git integration and service principal access if using a service principal.
7. Copy `terraform/terraform.tfvars.example` to `terraform/terraform.tfvars`.
8. Fill in every placeholder value.
9. Configure a remote Terraform backend before team use.
10. Run Terraform locally for first bootstrap, or create a temporary pipeline variable group containing `azureServiceConnection`.

## Azure DevOps Pipeline Notes

The `iac-platform` pipeline uses Terraform to manage Azure DevOps resources. The Azure DevOps provider is authenticated with `$(System.AccessToken)` as `AZDO_PERSONAL_ACCESS_TOKEN`.

Before this works:

- Enable script access to the OAuth token for the pipeline if your Azure DevOps organization requires it.
- Grant the Project Collection Build Service enough permission to manage build definitions and variable groups, or use a PAT-backed secure variable instead.
- Install/enable the Terraform pipeline task extension if `TerraformInstaller@1` is not already available.

## First Terraform Run

```bash
cd terraform
terraform init
terraform fmt -recursive
terraform validate
terraform plan -var-file terraform.tfvars
terraform apply -var-file terraform.tfvars
```

After Terraform applies successfully, it creates:

- Fabric Dev, Test, and Prod workspaces.
- Dev workspace Git integration.
- Fabric deployment pipeline stages.
- Workspace and deployment pipeline role assignments.
- Azure operational resources.
- Azure DevOps variable group.
- IaC and Fabric Azure Pipeline definitions.
