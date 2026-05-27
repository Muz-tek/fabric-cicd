# Fabric Spark Environments

Store Fabric Environment item definitions here when exported through Fabric Git integration.

Fabric serializes supported Environment settings into Git, including:

- Public libraries, usually represented as `environment.yml`.
- Custom library files.
- Spark compute settings, including Spark runtime and Spark properties.

Important deployment notes:

- Environment changes synced from Git enter the Environment staging state and must be published before they affect live notebook runs.
- The `fabric-cicd` pipeline syncs Dev from Git, then promotes Dev to Test and Test to Prod through Fabric deployment pipelines.
- Custom pools are not fully supported by Fabric deployment pipelines at the time of writing. If an Environment uses a custom pool, document and validate the target-environment compute behavior before production release.
- Keep environment-specific values in deployment rules or post-deployment automation, not hardcoded in notebook code.
