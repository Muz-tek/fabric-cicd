from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[1]
FABRIC_DIRS = [ROOT / "fabric", ROOT / "notebooks", ROOT / "pipelines"]


def validate_json_files() -> list[str]:
    errors: list[str] = []
    for base in FABRIC_DIRS:
        if not base.exists():
            continue
        for path in base.rglob("*.json"):
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"{path}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")
    return errors


def validate_notebooks() -> list[str]:
    errors: list[str] = []
    notebooks_dir = ROOT / "notebooks"
    if not notebooks_dir.exists():
        return errors

    notebook_paths = list(notebooks_dir.rglob("*.ipynb"))
    if not notebook_paths:
        return errors

    try:
        import nbformat
    except ImportError:
        return ["nbformat is required to validate notebooks"]

    for path in notebook_paths:
        try:
            nbformat.read(path, as_version=4)
        except Exception as exc:
            errors.append(f"{path}: invalid notebook: {exc}")
    return errors


def main() -> int:
    errors = validate_json_files() + validate_notebooks()
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Fabric artifact validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
