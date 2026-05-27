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


def request_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json",
    }


def poll_operation(url: str, headers: dict[str, str]) -> dict:
    for _ in range(80):
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code >= 400:
            raise RuntimeError(f"Fabric operation poll failed: {response.status_code} {response.text}")

        payload = response.json() if response.text else {}
        status = payload.get("status")
        if status in ("Succeeded", "Failed", "Cancelled"):
            return {"status": status, "operation": payload}

        retry_after = int(response.headers.get("Retry-After", "15"))
        time.sleep(retry_after)

    raise TimeoutError("Timed out waiting for Fabric deployment operation.")


def stage_id(stage_name: str) -> str:
    key = f"FABRIC_DEPLOYMENT_STAGE_ID_{stage_name.upper()}"
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


def deploy_stage(source: str, target: str, note: str) -> dict:
    deployment_pipeline_id = os.getenv("FABRIC_DEPLOYMENT_PIPELINE_ID")
    if not deployment_pipeline_id:
        raise RuntimeError("Missing required environment variable: FABRIC_DEPLOYMENT_PIPELINE_ID")

    headers = request_headers()
    body = {
        "sourceStageId": stage_id(source),
        "targetStageId": stage_id(target),
        "note": note[:1024],
    }

    response = requests.post(
        f"{FABRIC_API}/deploymentPipelines/{deployment_pipeline_id}/deploy",
        headers=headers,
        json=body,
        timeout=60,
    )

    if response.status_code not in (200, 202):
        raise RuntimeError(f"Fabric deployment failed: {response.status_code} {response.text}")

    operation_url = response.headers.get("Location") or response.headers.get("Operation-Location")
    if not operation_url:
        payload = response.json() if response.text else {}
        return {"status": "Succeeded", "response": payload}

    result = poll_operation(operation_url, headers)
    if result["status"] != "Succeeded":
        raise RuntimeError(f"Fabric deployment operation did not succeed: {result}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy between Fabric deployment pipeline stages.")
    parser.add_argument("--source", required=True, choices=["dev", "test"])
    parser.add_argument("--target", required=True, choices=["test", "prod"])
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    allowed_pairs = {("dev", "test"), ("test", "prod")}
    if (args.source, args.target) not in allowed_pairs:
        print("Only consecutive deployments are supported: dev->test or test->prod.", file=sys.stderr)
        return 1

    note = args.note or (
        f"Azure DevOps deployment {args.source}->{args.target}; "
        f"build={os.getenv('BUILD_BUILDID')}; commit={os.getenv('BUILD_SOURCEVERSION')}"
    )
    result = deploy_stage(args.source, args.target, note)

    EVIDENCE_DIR.mkdir(exist_ok=True)
    evidence = {
        "sourceStage": args.source,
        "targetStage": args.target,
        "timestampUtc": datetime.now(timezone.utc).isoformat(),
        "buildId": os.getenv("BUILD_BUILDID"),
        "sourceBranch": os.getenv("BUILD_SOURCEBRANCH"),
        "sourceVersion": os.getenv("BUILD_SOURCEVERSION"),
        "fabricDeployment": result,
    }
    output = EVIDENCE_DIR / f"fabric-deploy-{args.source}-to-{args.target}.json"
    output.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(f"Wrote release evidence to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
