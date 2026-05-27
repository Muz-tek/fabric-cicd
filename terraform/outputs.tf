output "fabric_workspace_ids" {
  description = "Fabric workspace IDs by environment."
  value       = { for env, workspace in fabric_workspace.env : env => workspace.id }
}

output "fabric_workspace_git_states" {
  description = "Git connection state by environment."
  value       = { for env, git in fabric_workspace_git.env : env => git.git_connection_state }
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
    ci      = azuredevops_build_definition.ci.name
    release = azuredevops_build_definition.release.name
  }
}
