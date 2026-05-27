# Fabric Access And Governance Model

## Access Model

Use Entra ID groups as the only durable assignment target. Avoid assigning individual users directly except for emergency break-glass access.

Recommended groups:

- `grp-fabric-platform-admins`: Fabric workspace Admin and deployment pipeline Admin.
- `grp-fabric-data-engineers`: Contributor in Dev and Test only.
- `grp-fabric-data-scientists`: Contributor in Dev and Test only, with governed access to curated Prod data.
- `grp-fabric-prod-viewers`: Viewer in Prod.
- `grp-fabric-gold-consumers`: access to curated Gold data products and semantic models.
- `grp-fabric-release-service-principals`: identities used by Azure Pipelines and automation.
- `grp-fabric-breakglass-admins`: emergency access, monitored and reviewed.

## Workspace Role Policy

- Dev: Admins, Data Engineers, and Data Scientists can develop and validate.
- Test: Admins, Data Engineers, and Data Scientists can validate deployment results and UAT.
- Prod: Admins are limited; most users are Viewers. No routine manual edits.

## Deployment Pipeline Access

The release identity needs:

- Admin role on the Fabric deployment pipeline.
- Contributor or higher on source and target workspaces.
- Permission to use the configured Fabric Git connection.

Service principal support depends on the item types included in the deployment. Validate this before relying on unattended deployment for a new Fabric item type.

## Data Access Policy

Workspace roles control Fabric item management. Data access should be governed separately:

- Use OneLake security roles for data access where applicable.
- Apply least privilege to Lakehouse and Warehouse data.
- Use separate Prod data access groups from Dev/Test groups.
- Restrict direct Bronze access in Prod to platform and data engineering support roles.
- Grant broader consumption through curated Gold data products, semantic models, and approved feature datasets.
- Keep secrets and credentials in managed connections or Key Vault-backed processes.
- Use semantic model RLS/OLS where BI access needs to differ by audience.
- Review shortcut permissions and external data source access before production release.

## Data Scientist Policy

Data scientists are first-class contributors in Dev and Test, but production access should be consumption-oriented unless a specific operational support role is approved.

- Dev: Data Scientists can create notebooks, experiments, feature engineering notebooks, and exploratory datasets.
- Test: Data Scientists can validate model features, Gold outputs, and performance against controlled data.
- Prod: Data Scientists should normally have Viewer access plus explicit data permissions to approved Gold datasets, feature tables, and semantic models.
- Production model scoring or feature generation should run through managed notebooks, Spark jobs, or Fabric pipelines deployed by `fabric-cicd`.
- Exploratory or ad hoc notebooks should not run directly against Prod Bronze data.

## Lakehouse Medallion Policy

The Lakehouse model uses Bronze, Silver, and Gold layers:

- Bronze: raw or lightly conformed source data. Preserve source fidelity, ingestion metadata, and lineage. Access is restricted.
- Silver: validated, standardized, deduplicated, and quality-checked data. This is the main engineering integration layer.
- Gold: curated business-ready data products, aggregates, features, and semantic-model-ready tables.

Governance expectations:

- Bronze writes are owned by ingestion pipelines and data engineering.
- Silver transformations require data quality checks and schema validation.
- Gold changes require product-owner review, semantic/data contract review, and downstream impact assessment.
- Data scientists should build features from Silver or Gold unless a raw-data exception is approved.
- Prod Bronze data is not a general exploration zone.
- Data quality failures block promotion before Prod.
- Deletions or breaking schema changes in Gold require explicit release notes and consumer communication.

## Spark And Compute Policy

- Use Fabric Environments for Spark runtime, library, and compute configuration.
- Pin public library versions and store custom libraries in Git.
- Publish Environments after Git sync before relying on them for notebook runs.
- Avoid custom pools in automated promotion until target behavior is verified, because custom pools are not fully supported in deployment pipelines.
- Production compute changes should go through pull request review and the Fabric deployment pipeline.

## Tenant, Capacity, And Workspace Policies

Manage these through Fabric admin and capacity admin processes:

- Tenant settings for Git integration and service principal access.
- Capacity delegated tenant settings.
- Workspace creation controls.
- External sharing and export controls.
- Sensitivity labels and endorsement/certification policy.
- Domain assignment and ownership.
- Monitoring and audit log retention.
- Managed private endpoints and connection governance.
- Tenant and capacity settings for Spark, pipelines, shortcuts, and OneLake behavior.

Where Fabric does not expose a stable Terraform or REST surface for a policy, keep the required setting in this document and validate it during platform readiness reviews.

## Change Control

- IaC changes go through the `iac-platform` pipeline.
- Fabric workload changes go through the `fabric-cicd` pipeline.
- Medallion layer contract changes are reviewed as Fabric workload changes.
- Prod deletions are manual and require a separate approved retirement change.
- Break-glass access must be time-limited and reviewed after use.
