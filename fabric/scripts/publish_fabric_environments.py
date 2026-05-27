import argparse
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "release-evidence"
FABRIC_API = "https://api.fabric.microsoft.com/v1"


def get_access_token() -> str:
    token = os.getenv("FABRIC_ACCESS_TOKEN")
    if token:
        return token

    result = subprocess.run(
        [
            "az",
            "account",
            "get-access-token",
            "--resource",
            "https://api.fabric.microsoft.com",
            "--query",
            "accessToken",
            "-o",
            "tsv",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def request_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json",
    }


def workspace_id(environment: str) -> str:
    key = f"FABRIC_WORKSPACE_ID_{environment.upper()}"
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


def get_all_items(workspace: str, headers: dict[str, str]) -> list[dict]:
    items: list[dict] = []
    url = f"{FABRIC_API}/workspaces/{workspace}/items?recursive=true"

    while url:
        response = requests.get(url, headers=headers, timeout=60)
        if response.status_code >= 400:
            raise RuntimeError(f"Fabric list items failed: {response.status_code} {response.text}")
        payload = response.json()
        items.extend(payload.get("value", []))
        url = payload.get("continuationUri")

    return items


def poll_operation(url: str, headers: dict[str, str]) -> dict:
    for _ in range(80):
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code >= 400:
            raise RuntimeError(f"Fabric environment publish poll failed: {response.status_code} {response.text}")

        payload = response.json() if response.text else {}
        status = payload.get("status")
        if status in ("Succeeded", "Failed", "Cancelled"):
            return {"status": status, "operation": payload}

        retry_after = int(response.headers.get("Retry-After", "15"))
        time.sleep(retry_after)

    raise TimeoutError("Timed out waiting for Fabric Environment publish operation.")


def publish_environment(workspace: str, environment_item: dict, headers: dict[str, str]) -> dict:
    item_id = environment_item["id"]
    response = requests.post(
        f"{FABRIC_API}/workspaces/{workspace}/environments/{item_id}/staging/publish",
        headers=headers,
        timeout=60,
    )

    if response.status_code in (200, 201):
        return {"status": "Succeeded", "item": environment_item}
    if response.status_code == 202:
        operation_url = response.headers.get("Location") or response.headers.get("Operation-Location")
        if not operation_url:
            return {"status": "Accepted", "item": environment_item, "response": response.text}
        result = poll_operation(operation_url, headers)
        result["item"] = environment_item
        return result

    if response.status_code == 400 and "No changes" in response.text:
        return {"status": "NoChanges", "item": environment_item}

    raise RuntimeError(
        f"Fabric Environment publish failed for {environment_item.get('displayName')}: "
        f"{response.status_code} {response.text}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish staged Fabric Environment items.")
    parser.add_argument("--environment", required=True, choices=["dev", "test", "prod"])
    args = parser.parse_args()

    workspace = workspace_id(args.environment)
    headers = request_headers()
    items = get_all_items(workspace, headers)
    environments = [item for item in items if item.get("type") == "Environment"]

    results = [publish_environment(workspace, item, headers) for item in environments]

    EVIDENCE_DIR.mkdir(exist_ok=True)
    evidence = {
        "environment": args.environment,
        "workspaceId": workspace,
        "timestampUtc": datetime.now(timezone.utc).isoformat(),
        "buildId": os.getenv("BUILD_BUILDID"),
        "sourceBranch": os.getenv("BUILD_SOURCEBRANCH"),
        "sourceVersion": os.getenv("BUILD_SOURCEVERSION"),
        "environmentCount": len(environments),
        "publishResults": results,
    }
    output = EVIDENCE_DIR / f"fabric-environment-publish-{args.environment}.json"
    output.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(f"Wrote Environment publish evidence to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
