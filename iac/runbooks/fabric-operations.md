# Microsoft Fabric DataOps Operational Runbooks

## Failed CI Validation

1. Open the failed Azure Pipeline run and identify the failed job.
2. For Terraform failures, download the `tfplan-*` artifact and review provider authentication, state lock, and variable values.
3. For Fabric artifact failures, run `python scripts/validate_fabric_items.py` locally and fix JSON or notebook formatting before retrying.
4. Re-run the pipeline from the same commit after the fix is merged.

## Failed Promotion

1. Confirm the target Azure DevOps environment approval was completed by an authorized approver.
2. Check the release evidence artifact for commit, branch, and target environment.
3. In Fabric, confirm the Dev workspace Git connection is `ConnectedAndInitialized`.
4. Confirm the Fabric deployment pipeline has Dev, Test, and Prod workspaces assigned to the correct stages.
5. If rollback is needed, revert or cherry-pick the Git commit, merge to the protected branch, and re-run the release pipeline.

## Production Item Retirement

1. Confirm the item is no longer required and identify downstream dependencies, schedules, reports, semantic models, and consumers.
2. Remove the item from the Fabric workload repo and deploy through Dev and Test.
3. Confirm Test validation passes without the retired item.
4. Raise a production retirement change with approval, rollback notes, and evidence.
5. Manually delete the target-only item from Prod after approval.
6. Record the deletion in release evidence or the change ticket.

## Production Incident

1. Capture incident start time, affected Fabric items, user impact, and last successful deployment.
2. Check Fabric workspace activity, pipeline run history, notebook execution history, and upstream data source availability.
3. Pause scheduled jobs if they may amplify bad data.
4. Restore service using the lowest-risk option: rerun source ingestion, roll back Git commit, restore data from validated storage, or disable downstream publication.
5. Record root cause, corrective action, and preventative action in the incident ticket.

## Access Request

1. Confirm the requester, business owner, target environment, and required role.
2. Prefer adding users to Entra ID groups mapped through Terraform variables rather than assigning individuals directly.
3. For production, require owner approval and least-privilege access.
4. Apply Terraform and verify the Fabric workspace role assignment.
