from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_dataops_folders_exist():
    required = [
        "azure-pipelines",
        "terraform",
        "scripts",
        "runbooks",
    ]

    for folder in required:
        assert (ROOT / folder).is_dir(), f"Missing required folder: {folder}"
