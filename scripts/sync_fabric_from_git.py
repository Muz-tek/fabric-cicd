import argparse
import json
import os
import subprocess
import sys
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


def poll_operation(url: str, headers: dict[str, str]) -> dict:
    for _ in range(60):
        poll = requests.get(url, headers=headers, timeout=30)
        if poll.status_code >= 400:
            raise RuntimeError(f"Fabric operation poll failed: {poll.status_code} {poll.text}")

        payload = poll.json() if poll.text else {}
        status = payload.get("status")
        if status in ("Succeeded", "Failed", "Cancelled"):
            return {"status": status, "operation": payload}

        retry_after = int(poll.headers.get("Retry-After", "10"))
        time.sleep(retry_after)

    raise TimeoutError("Timed out waiting for Fabric operation.")


def request_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json",
    }


def get_git_status(workspace_id: str, headers: dict[str, str]) -> dict:
    response = requests.get(
        f"{FABRIC_API}/workspaces/{workspace_id}/git/status",
        headers=headers,
        timeout=60,
    )
    if response.status_code == 202:
        operation_url = response.headers.get("Location") or response.headers.get("Operation-Location")
        if not operation_url:
            raise RuntimeError("Fabric get status returned 202 without an operation URL.")
        operation = poll_operation(operation_url, headers)
        if operation["status"] != "Succeeded":
            raise RuntimeError(f"Fabric get status operation did not succeed: {operation}")
        response = requests.get(
            f"{FABRIC_API}/workspaces/{workspace_id}/git/status",
            headers=headers,
            timeout=60,
        )

    if response.status_code >= 400:
        raise RuntimeError(f"Fabric git status failed: {response.status_code} {response.text}")
    return response.json()


def update_from_git(workspace_id: str) -> dict:
    headers = request_headers()
    status = get_git_status(workspace_id, headers)
    workspace_head = status.get("workspaceHead")
    remote_commit_hash = status.get("remoteCommitHash")

    if not remote_commit_hash:
        raise RuntimeError(f"Fabric git status did not include remoteCommitHash: {status}")

    if workspace_head == remote_commit_hash and not status.get("changes"):
        return {"status": "NoChanges", "gitStatus": status}

    body = {
        "workspaceHead": workspace_head,
        "remoteCommitHash": remote_commit_hash,
        "conflictResolution": {
            "conflictResolutionType": "Workspace",
            "conflictResolutionPolicy": "PreferRemote",
        },
        "options": {
            "allowOverrideItems": True,
        },
    }

    response = requests.post(
        f"{FABRIC_API}/workspaces/{workspace_id}/git/updateFromGit",
        headers=headers,
        json=body,
        timeout=60,
    )

    if response.status_code not in (200, 202):
        raise RuntimeError(f"Fabric updateFromGit failed: {response.status_code} {response.text}")

    operation_location = response.headers.get("Location") or response.headers.get("Operation-Location")
    if not operation_location:
        return {"status": "Completed", "gitStatus": status, "response": response.json() if response.text else {}}

    result = poll_operation(operation_location, headers)
    result["gitStatus"] = status
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Record Fabric Git sync release evidence.")
    parser.add_argument("--environment", required=True, choices=["dev", "test", "prod"])
    args = parser.parse_args()

    env_key = f"FABRIC_WORKSPACE_ID_{args.environment.upper()}"
    workspace_id = os.getenv(env_key)
    source_version = os.getenv("BUILD_SOURCEVERSION")

    if not workspace_id:
        print(f"Missing required environment variable: {env_key}", file=sys.stderr)
        return 1

    result = update_from_git(workspace_id)

    EVIDENCE_DIR.mkdir(exist_ok=True)
    evidence = {
        "environment": args.environment,
        "workspaceId": workspace_id,
        "timestampUtc": datetime.now(timezone.utc).isoformat(),
        "buildId": os.getenv("BUILD_BUILDID"),
        "sourceBranch": os.getenv("BUILD_SOURCEBRANCH"),
        "sourceVersion": source_version,
        "fabricUpdateFromGit": result,
    }
    output = EVIDENCE_DIR / f"fabric-sync-{args.environment}.json"
    output.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(f"Wrote release evidence to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
