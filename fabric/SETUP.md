# Fabric Workload Repo Setup

Copy the contents of this `fabric/` folder into the Azure DevOps Fabric workload repository.

## Required Inputs From Platform/IaC

The `iac-platform` Terraform deployment creates the shared variable group `vg-fabric-dataops`. The Fabric pipeline expects it to contain:

- `azureServiceConnection`
- `FABRIC_WORKSPACE_ID_DEV`
- `FABRIC_WORKSPACE_ID_TEST`
- `FABRIC_WORKSPACE_ID_PROD`
- `FABRIC_DEPLOYMENT_PIPELINE_ID`
- `FABRIC_DEPLOYMENT_STAGE_ID_DEV`
- `FABRIC_DEPLOYMENT_STAGE_ID_TEST`
- `FABRIC_DEPLOYMENT_STAGE_ID_PROD`

## Workload Folders

- `notebooks/`: Fabric notebooks.
- `pipelines/`: Fabric data pipelines.
- `environments/`: Spark Environment definitions.
- `lakehouses/`: Lakehouse definitions and metadata.
- `warehouses/`: Warehouse definitions and metadata.
- `dataflows/`: Dataflow definitions.
- `eventstreams/`: Eventstream definitions.
- `semantic-models/`: semantic model project files.
- `reports/`: report project files.
- `deployment-rules/`: environment-specific bindings and release-rule documentation.

## Pipeline Behavior

The `fabric-cicd` pipeline:

1. Validates workload files on pull requests and branch pushes.
2. Syncs the Dev Fabric workspace from `main`.
3. Publishes staged Fabric Spark Environments in Dev.
4. Deploys Dev to Test using `overwrite-test`.
5. Publishes staged Fabric Spark Environments in Test.
6. Deploys Test to Prod using `incremental-prod` after Azure DevOps approval.
7. Publishes staged Fabric Spark Environments in Prod.

Prod deployments do not delete target-only items. Retire Prod items manually through a separate approved change.

## Before First Release

1. Confirm the Dev workspace is connected to this repo and branch.
2. Confirm Test and Prod are assigned to the Fabric deployment pipeline stages.
3. Configure deployment rules for environment-specific values.
4. Authorize `vg-fabric-dataops` and the Azure service connection for the pipeline.
5. Add approval checks to the `fabric-prod` Azure DevOps Environment.
6. Validate service principal support for every Fabric item type included in the workload.
7. Confirm Bronze/Silver/Gold ownership, access, quality gates, and consumer-impact rules are documented in `lakehouses/MEDALLION.md`.
