data "azuredevops_project" "this" {
  name = var.azuredevops_project_name
}

data "azuredevops_git_repository" "iac" {
  project_id = data.azuredevops_project.this.id
  name       = var.azuredevops_iac_repository_name
}

data "azuredevops_git_repository" "fabric" {
  project_id = data.azuredevops_project.this.id
  name       = var.azuredevops_fabric_repository_name
}

resource "random_string" "suffix" {
  length  = 6
  upper   = false
  special = false
}

locals {
  normalized_project = lower(replace(var.project_name, "/[^a-zA-Z0-9]/", ""))
  resource_prefix    = local.normalized_project != "" ? local.normalized_project : "fabricdataops"
  name_stem          = substr(local.resource_prefix, 0, 12)
  key_vault_stem     = substr(local.resource_prefix, 0, 14)
  azdo_org_name      = trimsuffix(replace(var.azuredevops_org_service_url, "https://dev.azure.com/", ""), "/")
  environments       = toset(var.environment_names)
  non_prod_envs      = toset([for env in var.environment_names : env if env != "prod"])

  common_tags = {
    Application = var.project_name
    ManagedBy   = "Terraform"
    Workload    = "Microsoft Fabric DataOps"
  }
}

resource "azurerm_resource_group" "ops" {
  name     = "rg-${local.resource_prefix}-dataops"
  location = var.location
  tags     = local.common_tags
}

resource "azurerm_log_analytics_workspace" "ops" {
  name                = "law-${local.resource_prefix}-dataops"
  location            = azurerm_resource_group.ops.location
  resource_group_name = azurerm_resource_group.ops.name
  sku                 = "PerGB2018"
  retention_in_days   = var.log_retention_days
  tags                = local.common_tags
}

resource "azurerm_application_insights" "ops" {
  name                = "appi-${local.resource_prefix}-dataops"
  location            = azurerm_resource_group.ops.location
  resource_group_name = azurerm_resource_group.ops.name
  workspace_id        = azurerm_log_analytics_workspace.ops.id
  application_type    = "web"
  tags                = local.common_tags
}

resource "azurerm_storage_account" "artifacts" {
  name                     = "st${local.name_stem}${random_string.suffix.result}"
  resource_group_name      = azurerm_resource_group.ops.name
  location                 = azurerm_resource_group.ops.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"

  blob_properties {
    versioning_enabled = true

    delete_retention_policy {
      days = 14
    }

    container_delete_retention_policy {
      days = 14
    }
  }

  tags = local.common_tags
}

resource "azurerm_storage_container" "releases" {
  name                  = "fabric-releases"
  storage_account_id    = azurerm_storage_account.artifacts.id
  container_access_type = "private"
}

resource "azurerm_key_vault" "ops" {
  name                       = "kv-${local.key_vault_stem}-${random_string.suffix.result}"
  location                   = azurerm_resource_group.ops.location
  resource_group_name        = azurerm_resource_group.ops.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 14
  purge_protection_enabled   = true
  enable_rbac_authorization  = true
  tags                       = local.common_tags
}

data "azurerm_client_config" "current" {}

resource "fabric_workspace" "env" {
  for_each     = local.environments
  display_name = "${var.project_name}-${each.key}"
  description  = "Managed ${each.key} workspace for ${var.project_name} Fabric DataOps."
  capacity_id  = var.fabric_capacity_id
}

resource "fabric_workspace_git" "dev" {
  workspace_id            = fabric_workspace.env["dev"].id
  initialization_strategy = "PreferRemote"

  git_provider_details = {
    git_provider_type = "AzureDevOps"
    organization_name = local.azdo_org_name
    project_name      = var.azuredevops_project_name
    repository_name   = var.azuredevops_fabric_repository_name
    branch_name       = var.dev_git_branch
    directory_name    = var.git_directory
  }

  git_credentials = {
    source        = "ConfiguredConnection"
    connection_id = var.fabric_git_connection_id
  }
}

resource "fabric_deployment_pipeline" "release" {
  display_name = "${var.project_name}-fabric-release"
  description  = "Azure DevOps-controlled Fabric deployment pipeline for ${var.project_name}."

  stages = [
    {
      display_name = "Dev"
      description  = "Git-connected development stage."
      is_public    = false
      workspace_id = fabric_workspace.env["dev"].id
    },
    {
      display_name = "Test"
      description  = "Controlled test stage promoted from Dev."
      is_public    = false
      workspace_id = fabric_workspace.env["test"].id
    },
    {
      display_name = "Prod"
      description  = "Controlled production stage promoted from Test."
      is_public    = false
      workspace_id = fabric_workspace.env["prod"].id
    }
  ]
}

resource "fabric_lakehouse" "bronze" {
  for_each     = var.create_sample_lakehouse ? local.environments : toset([])
  workspace_id = fabric_workspace.env[each.key].id
  display_name = "lh_${replace(var.project_name, "-", "_")}_${each.key}_bronze"
  description  = "Baseline raw/bronze Lakehouse managed by Terraform."

  configuration = {
    enable_schemas = true
  }
}

resource "fabric_workspace_role_assignment" "admins" {
  for_each = {
    for item in flatten([
      for env in var.environment_names : [
        for principal_id in var.workspace_admin_principal_ids : {
          key          = "${env}-${principal_id}"
          env          = env
          principal_id = principal_id
        }
      ]
    ]) : item.key => item
  }

  workspace_id = fabric_workspace.env[each.value.env].id
  principal = {
    id   = each.value.principal_id
    type = "Group"
  }
  role = "Admin"
}

resource "fabric_workspace_role_assignment" "contributors" {
  for_each = {
    for item in flatten([
      for env in local.non_prod_envs : [
        for principal_id in var.workspace_contributor_principal_ids : {
          key          = "${env}-${principal_id}"
          env          = env
          principal_id = principal_id
        }
      ]
    ]) : item.key => item
  }

  workspace_id = fabric_workspace.env[each.value.env].id
  principal = {
    id   = each.value.principal_id
    type = "Group"
  }
  role = "Contributor"
}

resource "fabric_deployment_pipeline_role_assignment" "admins" {
  for_each = toset(var.deployment_pipeline_admin_principal_ids)

  deployment_pipeline_id = fabric_deployment_pipeline.release.id
  principal = {
    id   = each.value
    type = "Group"
  }
  role = "Admin"
}

resource "azuredevops_variable_group" "platform" {
  project_id   = data.azuredevops_project.this.id
  name         = "vg-fabric-dataops"
  description  = "Shared variables for Fabric DataOps pipelines."
  allow_access = false

  variable {
    name  = "azureServiceConnection"
    value = var.azure_service_connection_name
  }

  variable {
    name  = "artifactStorageAccount"
    value = azurerm_storage_account.artifacts.name
  }

  variable {
    name  = "artifactContainer"
    value = azurerm_storage_container.releases.name
  }

  variable {
    name  = "logAnalyticsWorkspaceId"
    value = azurerm_log_analytics_workspace.ops.workspace_id
  }

  dynamic "variable" {
    for_each = fabric_workspace.env
    content {
      name  = "FABRIC_WORKSPACE_ID_${upper(variable.key)}"
      value = variable.value.id
    }
  }

  variable {
    name  = "FABRIC_DEPLOYMENT_PIPELINE_ID"
    value = fabric_deployment_pipeline.release.id
  }

  variable {
    name  = "FABRIC_DEPLOYMENT_STAGE_ID_DEV"
    value = fabric_deployment_pipeline.release.stages[0].id
  }

  variable {
    name  = "FABRIC_DEPLOYMENT_STAGE_ID_TEST"
    value = fabric_deployment_pipeline.release.stages[1].id
  }

  variable {
    name  = "FABRIC_DEPLOYMENT_STAGE_ID_PROD"
    value = fabric_deployment_pipeline.release.stages[2].id
  }
}

resource "azuredevops_build_definition" "ci" {
  project_id = data.azuredevops_project.this.id
  name       = "${var.project_name}-iac-platform"
  path       = "\\Fabric DataOps"

  repository {
    repo_type   = "TfsGit"
    repo_id     = data.azuredevops_git_repository.iac.id
    branch_name = "refs/heads/main"
    yml_path    = "azure-pipelines/iac-platform.yml"
  }
}

resource "azuredevops_build_definition" "fabric" {
  project_id = data.azuredevops_project.this.id
  name       = "${var.project_name}-fabric-cicd"
  path       = "\\Fabric DataOps"

  repository {
    repo_type   = "TfsGit"
    repo_id     = data.azuredevops_git_repository.fabric.id
    branch_name = "refs/heads/main"
    yml_path    = "azure-pipelines/fabric-cicd.yml"
  }
}
