#!/usr/bin/env python3
"""
GitHub Actions Deployment Monitor

Polls GitHub Actions workflow runs until deployment completes.
Part of the QA Loop workflow for automated Power BI validation.

Usage:
    python monitor_deployment_status.py --repo <owner/repo> --commit <sha> [options]

Options:
    --repo <owner/repo>     GitHub repository (required)
    --commit <sha>          Commit SHA to monitor (required)
    --workflow <name>       Workflow file name (default: deploy.yml)
    --timeout <seconds>     Timeout in seconds (default: 600)
    --interval <seconds>    Poll interval in seconds (default: 30)
    --json                  Output in JSON format

Exit Codes:
    0 - Deployment succeeded
    1 - Deployment failed
    2 - Deployment timed out
    3 - Script error

Author: Power BI Analyst Agent
Version: 1.0.0
"""

import subprocess
import time
import json
import sys
import argparse
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime


@dataclass
class DeploymentStatus:
    """Represents the current deployment status"""
    status: str  # "pending", "in_progress", "success", "failure", "timeout", "error"
    conclusion: Optional[str]
    duration_seconds: int
    workflow_run_id: Optional[int]
    logs_url: Optional[str]
    error_message: Optional[str]
    timestamp: str

    def to_dict(self):
        return asdict(self)


class GitHubActionsMonitor:
    """
    Monitor GitHub Actions deployment workflow.

    Uses the GitHub CLI (`gh`) to query workflow run status.
    Requires `gh` to be installed and authenticated.
    """

    def __init__(
        self,
        repo: str,
        commit_sha: str,
        workflow_name: str = "deploy.yml",
        timeout_seconds: int = 600,
        poll_interval: int = 30,
        verbose: bool = True
    ):
        self.repo = repo
        self.commit_sha = commit_sha
        self.workflow_name = workflow_name
        self.timeout_seconds = timeout_seconds
        self.poll_interval = poll_interval
        self.verbose = verbose

    def _log(self, message: str):
        """Print log message if verbose mode is enabled"""
        if self.verbose:
            print(f"   {message}")

    def check_gh_cli(self) -> bool:
        """Check if GitHub CLI is available and authenticated"""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def monitor(self) -> DeploymentStatus:
        """
        Poll until deployment completes or times out.

        Returns:
            DeploymentStatus with final state
        """
        # Check GitHub CLI availability
        if not self.check_gh_cli():
            return DeploymentStatus(
                status="error",
                conclusion=None,
                duration_seconds=0,
                workflow_run_id=None,
                logs_url=None,
                error_message="GitHub CLI (gh) not available or not authenticated. Run 'gh auth login' to authenticate.",
                timestamp=datetime.now().isoformat()
            )

        start_time = time.time()
        self._log(f"Monitoring deployment for commit {self.commit_sha[:8]}...")
        self._log(f"Repository: {self.repo}")
        self._log(f"Workflow: {self.workflow_name}")
        self._log(f"Timeout: {self.timeout_seconds}s")

        # Initial wait for workflow to start
        self._log("Waiting for workflow to start...")
        time.sleep(5)

        while True:
            elapsed = int(time.time() - start_time)

            if elapsed > self.timeout_seconds:
                return DeploymentStatus(
                    status="timeout",
                    conclusion=None,
                    duration_seconds=elapsed,
                    workflow_run_id=None,
                    logs_url=None,
                    error_message=f"Deployment timed out after {self.timeout_seconds}s",
                    timestamp=datetime.now().isoformat()
                )

            # Query workflow status
            status = self._get_workflow_status()

            if status.status == "success":
                self._log(f"Deployment completed successfully in {elapsed}s")
                status.duration_seconds = elapsed
                return status

            if status.status == "failure":
                self._log(f"Deployment failed after {elapsed}s")
                status.duration_seconds = elapsed
                return status

            if status.status == "error":
                return status

            # Still in progress
            self._log(f"Status: {status.status} ({elapsed}s elapsed)")
            time.sleep(self.poll_interval)

    def _get_workflow_status(self) -> DeploymentStatus:
        """Query GitHub Actions API via gh CLI"""
        try:
            # Query workflow runs for the commit
            result = subprocess.run(
                [
                    "gh", "run", "list",
                    "--repo", self.repo,
                    "--workflow", self.workflow_name,
                    "--json", "status,conclusion,databaseId,url,headSha",
                    "--limit", "10"
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                # Try without workflow filter in case name doesn't match
                result = subprocess.run(
                    [
                        "gh", "run", "list",
                        "--repo", self.repo,
                        "--json", "status,conclusion,databaseId,url,headSha",
                        "--limit", "10"
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

            if result.returncode != 0:
                return DeploymentStatus(
                    status="error",
                    conclusion=None,
                    duration_seconds=0,
                    workflow_run_id=None,
                    logs_url=None,
                    error_message=f"Failed to query GitHub Actions: {result.stderr}",
                    timestamp=datetime.now().isoformat()
                )

            runs = json.loads(result.stdout)

            # Find run for our commit
            matching_run = None
            for run in runs:
                if run.get("headSha", "").startswith(self.commit_sha[:7]):
                    matching_run = run
                    break

            if not matching_run:
                # No matching run found yet - workflow may not have started
                return DeploymentStatus(
                    status="pending",
                    conclusion=None,
                    duration_seconds=0,
                    workflow_run_id=None,
                    logs_url=None,
                    error_message=None,
                    timestamp=datetime.now().isoformat()
                )

            # Map GitHub status to our status
            gh_status = matching_run.get("status", "unknown")
            gh_conclusion = matching_run.get("conclusion")

            if gh_status == "completed":
                if gh_conclusion == "success":
                    status = "success"
                else:
                    status = "failure"
            elif gh_status in ("queued", "waiting"):
                status = "pending"
            elif gh_status == "in_progress":
                status = "in_progress"
            else:
                status = "pending"

            return DeploymentStatus(
                status=status,
                conclusion=gh_conclusion,
                duration_seconds=0,
                workflow_run_id=matching_run.get("databaseId"),
                logs_url=matching_run.get("url"),
                error_message=None,
                timestamp=datetime.now().isoformat()
            )

        except subprocess.TimeoutExpired:
            return DeploymentStatus(
                status="error",
                conclusion=None,
                duration_seconds=0,
                workflow_run_id=None,
                logs_url=None,
                error_message="Timeout querying GitHub Actions API",
                timestamp=datetime.now().isoformat()
            )
        except json.JSONDecodeError as e:
            return DeploymentStatus(
                status="error",
                conclusion=None,
                duration_seconds=0,
                workflow_run_id=None,
                logs_url=None,
                error_message=f"Failed to parse GitHub API response: {str(e)}",
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return DeploymentStatus(
                status="error",
                conclusion=None,
                duration_seconds=0,
                workflow_run_id=None,
                logs_url=None,
                error_message=f"Unexpected error: {str(e)}",
                timestamp=datetime.now().isoformat()
            )

    def get_workflow_logs(self, run_id: int) -> Optional[str]:
        """Fetch workflow logs for a specific run"""
        try:
            result = subprocess.run(
                [
                    "gh", "run", "view",
                    str(run_id),
                    "--repo", self.repo,
                    "--log"
                ],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                return result.stdout
            return None
        except Exception:
            return None


def print_report(status: DeploymentStatus):
    """Print deployment status report to console"""
    print("=" * 80)
    print("DEPLOYMENT STATUS REPORT")
    print("=" * 80)
    print(f"Timestamp: {status.timestamp}")
    print(f"Status: {status.status.upper()}")

    if status.conclusion:
        print(f"Conclusion: {status.conclusion}")

    if status.duration_seconds:
        print(f"Duration: {status.duration_seconds}s")

    if status.workflow_run_id:
        print(f"Run ID: {status.workflow_run_id}")

    if status.logs_url:
        print(f"Logs: {status.logs_url}")

    if status.error_message:
        print(f"\nError: {status.error_message}")

    print("=" * 80)

    if status.status == "success":
        print("\n[SUCCESS] Deployment completed successfully!")
        print("The Power BI report has been deployed and is ready for inspection.")
    elif status.status == "failure":
        print("\n[FAILED] Deployment failed!")
        print("Check the workflow logs for details.")
    elif status.status == "timeout":
        print("\n[TIMEOUT] Deployment monitoring timed out!")
        print("The deployment may still be in progress. Check GitHub Actions directly.")
    elif status.status == "error":
        print("\n[ERROR] Failed to monitor deployment!")
        print("Check the error message above for details.")

    print("=" * 80)


def main():
    """Main entry point for command-line usage"""
    parser = argparse.ArgumentParser(
        description="Monitor GitHub Actions deployment workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python monitor_deployment_status.py --repo owner/repo --commit abc123
  python monitor_deployment_status.py --repo owner/repo --commit abc123 --workflow deploy.yml
  python monitor_deployment_status.py --repo owner/repo --commit abc123 --timeout 300 --json

Exit Codes:
  0 - Deployment succeeded
  1 - Deployment failed
  2 - Deployment timed out
  3 - Script error
        """
    )

    parser.add_argument("--repo", required=True, help="GitHub repository (owner/repo)")
    parser.add_argument("--commit", required=True, help="Commit SHA to monitor")
    parser.add_argument("--workflow", default="deploy.yml", help="Workflow file name (default: deploy.yml)")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout in seconds (default: 600)")
    parser.add_argument("--interval", type=int, default=30, help="Poll interval in seconds (default: 30)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    try:
        monitor = GitHubActionsMonitor(
            repo=args.repo,
            commit_sha=args.commit,
            workflow_name=args.workflow,
            timeout_seconds=args.timeout,
            poll_interval=args.interval,
            verbose=not args.json
        )

        status = monitor.monitor()

        if args.json:
            print(json.dumps(status.to_dict(), indent=2))
        else:
            print_report(status)

        # Exit codes
        if status.status == "success":
            sys.exit(0)
        elif status.status == "failure":
            sys.exit(1)
        elif status.status == "timeout":
            sys.exit(2)
        else:
            sys.exit(3)

    except Exception as e:
        if args.json:
            print(json.dumps({
                "status": "error",
                "error_message": str(e)
            }))
        else:
            print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
