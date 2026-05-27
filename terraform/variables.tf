variable "project_name" {
  description = "Short project/application name used in resource names."
  type        = string
}

variable "location" {
  description = "Azure region for supporting Azure resources."
  type        = string
  default     = "australiaeast"
}

variable "environment_names" {
  description = "Fabric environments to create and promote through."
  type        = list(string)
  default     = ["dev", "test", "prod"]
}

variable "fabric_capacity_id" {
  description = "Existing Microsoft Fabric capacity ID to assign to each workspace."
  type        = string
}

variable "fabric_git_connection_id" {
  description = "Fabric configured connection ID for Azure DevOps Git integration."
  type        = string
}

variable "azuredevops_org_service_url" {
  description = "Azure DevOps organization URL, for example https://dev.azure.com/contoso."
  type        = string
}

variable "azuredevops_project_name" {
  description = "Azure DevOps project name."
  type        = string
}

variable "azuredevops_repository_name" {
  description = "Azure Repos repository name containing the Fabric source."
  type        = string
}

variable "azure_service_connection_name" {
  description = "Name of the Azure Resource Manager service connection used by Azure Pipelines."
  type        = string
}

variable "git_directory" {
  description = "Repository folder synced to Fabric workspaces."
  type        = string
  default     = "/fabric"

  validation {
    condition     = startswith(var.git_directory, "/")
    error_message = "git_directory must start with '/'."
  }
}

variable "branch_by_environment" {
  description = "Git branch mapped to each Fabric workspace."
  type        = map(string)
  default = {
    dev  = "develop"
    test = "release/test"
    prod = "main"
  }
}

variable "workspace_admin_principal_ids" {
  description = "Extra Entra ID principal IDs granted Admin in each Fabric workspace."
  type        = list(string)
  default     = []
}

variable "workspace_contributor_principal_ids" {
  description = "Extra Entra ID principal IDs granted Contributor in non-production Fabric workspaces."
  type        = list(string)
  default     = []
}

variable "create_sample_lakehouse" {
  description = "Create a baseline Lakehouse in each Fabric workspace."
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Retention period for operational logs."
  type        = number
  default     = 90
}
