#!/usr/bin/env python3
"""
Agent Logger - Hook handler for tracking Power BI plugin agent execution.

This script is called by Claude Code hooks (PreToolUse and PostToolUse) to:
1. Track when plugin agents start and complete
2. Calculate execution duration
3. Log metrics to runtime_events.jsonl

Usage:
    Called automatically by Claude Code hooks configured in settings.json
    Receives JSON payload via stdin
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
# Note: File locking omitted for simplicity - hook calls are typically sequential

# Plugin agent names (extracted from .claude/agents/*.md)
PLUGIN_AGENTS = {
    "power-bi-verification",
    "powerbi-artifact-designer",
    "powerbi-code-fix-identifier",
    "powerbi-code-implementer-apply",
    "powerbi-code-locator",
    "powerbi-code-merger",
    "powerbi-code-understander",
    "powerbi-compare-project-code",
    "powerbi-dashboard-update-planner",
    "powerbi-data-context-agent",
    "powerbi-data-model-analyzer",
    "powerbi-dax-review-agent",
    "powerbi-pattern-discovery",
    "powerbi-playwright-tester",
    "powerbi-tmdl-syntax-validator",
    "powerbi-verify-pbiproject-folder-setup",
    "powerbi-visual-locator",
    "powerbi-page-question-analyzer",
    "powerbi-visual-type-recommender",
    "powerbi-page-layout-designer",
    "powerbi-interaction-designer",
    "powerbi-artifact-decomposer",
    "powerbi-data-understanding-agent",
    "power-bi-visual-edit-planner",
    "powerbi-pbir-page-generator",
    "powerbi-pbir-validator",
    "powerbi-visual-implementer-apply",
}


def get_analytics_dir() -> Path:
    """Get analytics directory, respecting environment variable override."""
    env_path = os.environ.get("POWERBI_ANALYST_ANALYTICS_PATH")
    if env_path:
        return Path(env_path)

    # Default: relative to cwd (project root)
    return Path("agent_scratchpads/_analytics")


def get_inflight_path() -> Path:
    """Get path to in-flight tasks storage."""
    analytics_dir = get_analytics_dir()
    analytics_dir.mkdir(parents=True, exist_ok=True)
    return analytics_dir / ".inflight_tasks.json"


def get_runtime_log_path() -> Path:
    """Get path to runtime events log."""
    analytics_dir = get_analytics_dir()
    analytics_dir.mkdir(parents=True, exist_ok=True)
    return analytics_dir / "runtime_events.jsonl"


def load_inflight_tasks() -> dict:
    """Load in-flight tasks from storage."""
    path = get_inflight_path()
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_inflight_tasks(tasks: dict) -> None:
    """Save in-flight tasks to storage."""
    path = get_inflight_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tasks, f)


def append_runtime_event(event: dict) -> None:
    """Append event to runtime log (JSONL format)."""
    path = get_runtime_log_path()
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def handle_pre_tool_use(payload: dict) -> None:
    """Handle PreToolUse event - record start time."""
    tool_use_id = payload.get("tool_use_id")
    tool_input = payload.get("tool_input", {})
    subagent_type = tool_input.get("subagent_type", "")

    # Only track plugin agents
    if subagent_type not in PLUGIN_AGENTS:
        return

    # Store start time and metadata
    inflight = load_inflight_tasks()
    inflight[tool_use_id] = {
        "start_time": datetime.utcnow().isoformat() + "Z",
        "session_id": payload.get("session_id", ""),
        "agent_name": subagent_type,
        "prompt_preview": (tool_input.get("prompt", "")[:200] + "..."
                          if len(tool_input.get("prompt", "")) > 200
                          else tool_input.get("prompt", "")),
        "cwd": payload.get("cwd", ""),
    }
    save_inflight_tasks(inflight)


def handle_post_tool_use(payload: dict) -> None:
    """Handle PostToolUse event - calculate duration and log."""
    tool_use_id = payload.get("tool_use_id")

    # Load in-flight tasks
    inflight = load_inflight_tasks()

    # Check if we have a matching start event
    if tool_use_id not in inflight:
        # Either not a plugin agent or PreToolUse wasn't captured
        return

    start_data = inflight.pop(tool_use_id)
    save_inflight_tasks(inflight)

    # Calculate duration
    start_time = datetime.fromisoformat(start_data["start_time"].rstrip("Z"))
    end_time = datetime.utcnow()
    duration_seconds = (end_time - start_time).total_seconds()

    # Create runtime event
    event = {
        "timestamp": end_time.isoformat() + "Z",
        "session_id": start_data["session_id"],
        "agent_name": start_data["agent_name"],
        "start_time": start_data["start_time"],
        "end_time": end_time.isoformat() + "Z",
        "duration_seconds": round(duration_seconds, 3),
        "prompt_preview": start_data["prompt_preview"],
        "tool_use_id": tool_use_id,
        "cwd": start_data["cwd"],
    }

    # Append to log
    append_runtime_event(event)

    # Output to stderr for visibility (optional, won't affect hook behavior)
    print(f"[AGENT_LOG] {event['agent_name']}: {duration_seconds:.1f}s", file=sys.stderr)


def main():
    """Main entry point - reads hook payload from stdin."""
    try:
        # Read JSON from stdin
        input_data = sys.stdin.read()
        if not input_data.strip():
            sys.exit(0)

        payload = json.loads(input_data)

        # Only process Task tool calls
        if payload.get("tool_name") != "Task":
            sys.exit(0)

        # Route to appropriate handler
        hook_event = payload.get("hook_event_name", "")

        if hook_event == "PreToolUse":
            handle_pre_tool_use(payload)
        elif hook_event == "PostToolUse":
            handle_post_tool_use(payload)

        sys.exit(0)

    except Exception as e:
        # Log error but don't block Claude Code
        print(f"[AGENT_LOG ERROR] {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
