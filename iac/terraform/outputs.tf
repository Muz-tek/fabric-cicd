output "fabric_workspace_ids" {
  description = "Fabric workspace IDs by environment."
  value       = { for env, workspace in fabric_workspace.env : env => workspace.id }
}

output "fabric_dev_workspace_git_state" {
  description = "Git connection state for the Fabric dev workspace."
  value       = fabric_workspace_git.dev.git_connection_state
}

output "fabric_deployment_pipeline_id" {
  description = "Fabric deployment pipeline ID used for Dev to Test to Prod promotion."
  value       = fabric_deployment_pipeline.release.id
}

output "fabric_deployment_pipeline_stage_ids" {
  description = "Fabric deployment pipeline stage IDs by environment."
  value = {
    dev  = fabric_deployment_pipeline.release.stages[0].id
    test = fabric_deployment_pipeline.release.stages[1].id
    prod = fabric_deployment_pipeline.release.stages[2].id
  }
}

output "release_storage_account_name" {
  description = "Storage account used for release evidence and artifacts."
  value       = azurerm_storage_account.artifacts.name
}

output "azuredevops_variable_group_name" {
  description = "Variable group created for Azure Pipelines."
  value       = azuredevops_variable_group.platform.name
}

output "pipeline_names" {
  description = "Created Azure Pipeline definitions."
  value = {
    iac_platform = azuredevops_build_definition.ci.name
    fabric_cicd  = azuredevops_build_definition.fabric.name
  }
}
