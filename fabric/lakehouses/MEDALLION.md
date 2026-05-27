# Lakehouse Medallion Architecture

This workload uses a Bronze, Silver, and Gold Lakehouse model.

## Bronze

Purpose:

- Raw or lightly conformed source data.
- Source fidelity and ingestion lineage.
- Replay and recovery support.

Governance:

- Restricted access in Prod.
- Owned by ingestion and data engineering.
- No general ad hoc analysis in Prod Bronze.
- Schema drift is captured and reviewed before promotion.

## Silver

Purpose:

- Cleaned, validated, deduplicated, standardized data.
- Shared engineering integration layer.
- Preferred input for feature engineering and downstream transformations.

Governance:

- Data quality checks are required.
- Schema and contract changes are reviewed in pull requests.
- PII handling and masking rules are applied before data is promoted to Gold where appropriate.

## Gold

Purpose:

- Curated business-ready data products.
- BI-ready tables and semantic model inputs.
- Approved feature tables for data science and ML workloads.

Governance:

- Consumer-facing changes require product-owner review.
- Breaking schema changes require release notes and downstream impact assessment.
- Access is broader than Bronze/Silver but still least-privilege.
- Prod deletes are manual and require a retirement change.

## Data Science Usage

- Data scientists should use Silver or Gold by default.
- Direct Prod Bronze access requires an approved exception.
- Feature tables promoted to Gold should have owner, refresh, lineage, and quality expectations documented.
