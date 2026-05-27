from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_fabric_folders_exist():
    required = [
        "azure-pipelines",
        "dataflows",
        "deployment-rules",
        "environments",
        "eventstreams",
        "items",
        "lakehouses",
        "notebooks",
        "pipelines",
        "reports",
        "scripts",
        "semantic-models",
    ]

    for folder in required:
        assert (ROOT / folder).is_dir(), f"Missing required folder: {folder}"


def test_required_fabric_scripts_exist():
    required = [
        "azure-pipelines/fabric-cicd.yml",
        "azure-pipelines/templates/fabric-validate.yml",
        "azure-pipelines/templates/fabric-sync-dev.yml",
        "azure-pipelines/templates/fabric-promote.yml",
        "scripts/validate_fabric_items.py",
        "scripts/sync_fabric_from_git.py",
        "scripts/deploy_fabric_stage.py",
    ]

    for file_path in required:
        assert (ROOT / file_path).is_file(), f"Missing required file: {file_path}"
