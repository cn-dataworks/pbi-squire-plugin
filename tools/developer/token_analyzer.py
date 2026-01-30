#!/usr/bin/env python3
"""
Token Analyzer - Parse Claude Code JSONL logs for token usage data.

This script reads Claude Code's session logs and extracts token usage
information for plugin agent invocations, correlating with runtime events.

Usage:
    python token_analyzer.py [--session SESSION_ID] [--since HOURS]

Options:
    --session   Analyze specific session only
    --since     Analyze logs from last N hours (default: 24)
"""

import json
import sys
import os
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Generator, Dict, List
import glob


def get_claude_logs_dir() -> Path:
    """Get Claude Code logs directory for current platform."""
    if sys.platform == "win32":
        # Windows: C:\Users\<username>\.claude\projects\
        home = Path(os.environ.get("USERPROFILE", ""))
    else:
        # Unix: ~/.claude/projects/
        home = Path(os.environ.get("HOME", ""))

    return home / ".claude" / "projects"


def get_analytics_dir() -> Path:
    """Get analytics directory, respecting environment variable override."""
    env_path = os.environ.get("POWERBI_ANALYST_ANALYTICS_PATH")
    if env_path:
        return Path(env_path)
    return Path("agent_scratchpads/_analytics")


def get_token_log_path() -> Path:
    """Get path to token usage log."""
    analytics_dir = get_analytics_dir()
    analytics_dir.mkdir(parents=True, exist_ok=True)
    return analytics_dir / "token_usage.jsonl"


def get_last_analysis_path() -> Path:
    """Get path to last analysis timestamp file."""
    analytics_dir = get_analytics_dir()
    return analytics_dir / ".last_token_analysis"


def get_last_analysis_time() -> Optional[datetime]:
    """Get timestamp of last analysis run."""
    path = get_last_analysis_path()
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                timestamp = f.read().strip()
                return datetime.fromisoformat(timestamp)
        except (ValueError, IOError):
            return None
    return None


def save_last_analysis_time() -> None:
    """Save current timestamp as last analysis time."""
    path = get_last_analysis_path()
    with open(path, "w", encoding="utf-8") as f:
        f.write(datetime.utcnow().isoformat())


def find_jsonl_files(logs_dir: Path, since: datetime) -> Generator[Path, None, None]:
    """Find JSONL log files modified since given time."""
    if not logs_dir.exists():
        return

    # Search recursively for .jsonl files
    for jsonl_file in logs_dir.rglob("*.jsonl"):
        try:
            mtime = datetime.fromtimestamp(jsonl_file.stat().st_mtime)
            if mtime >= since:
                yield jsonl_file
        except OSError:
            continue


def parse_jsonl_file(file_path: Path) -> Generator[dict, None, None]:
    """Parse a JSONL file and yield records."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    except IOError:
        return


def extract_task_token_usage(records: Generator[dict, None, None]) -> List[dict]:
    """
    Extract token usage for Task tool invocations from JSONL records.

    Claude Code JSONL format includes:
    - message.role: "assistant" or "user"
    - message.usage: { input_tokens, output_tokens }
    - toolUseResult: results from tool calls
    """
    token_events = []

    # Track state across records to correlate tool calls with responses
    pending_tool_calls = {}  # tool_use_id -> { timestamp, tool_input }

    for record in records:
        timestamp = record.get("timestamp", "")
        message = record.get("message", {})

        # Look for tool use in assistant messages
        if message.get("role") == "assistant":
            content = message.get("content", [])
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "tool_use":
                        tool_name = item.get("name", "")
                        if tool_name == "Task":
                            tool_use_id = item.get("id", "")
                            tool_input = item.get("input", {})
                            pending_tool_calls[tool_use_id] = {
                                "timestamp": timestamp,
                                "subagent_type": tool_input.get("subagent_type", "unknown"),
                                "prompt_preview": (tool_input.get("prompt", "")[:100]
                                                   if tool_input.get("prompt") else ""),
                            }

        # Look for tool results
        tool_result = record.get("toolUseResult")
        if tool_result:
            tool_use_id = tool_result.get("toolUseId", "")
            if tool_use_id in pending_tool_calls:
                call_info = pending_tool_calls.pop(tool_use_id)

                # Extract usage if available in the result
                usage = record.get("usage", {})
                if not usage:
                    # Sometimes usage is at message level
                    usage = message.get("usage", {})

                if usage:
                    token_events.append({
                        "timestamp": call_info["timestamp"],
                        "agent_name": call_info["subagent_type"],
                        "input_tokens": usage.get("input_tokens", 0),
                        "output_tokens": usage.get("output_tokens", 0),
                        "total_tokens": (usage.get("input_tokens", 0) +
                                         usage.get("output_tokens", 0)),
                        "tool_use_id": tool_use_id,
                        "prompt_preview": call_info["prompt_preview"],
                    })

        # Alternative: Look for usage at record level (varies by Claude Code version)
        usage = record.get("usage")
        if usage and not token_events:
            # This might be aggregate usage - harder to attribute to specific tools
            pass

    return token_events


def load_runtime_events() -> List[dict]:
    """Load runtime events log for correlation."""
    runtime_path = get_analytics_dir() / "runtime_events.jsonl"
    events = []
    if runtime_path.exists():
        for record in parse_jsonl_file(runtime_path):
            events.append(record)
    return events


def correlate_with_runtime(token_events: List[dict], runtime_events: List[dict]) -> List[dict]:
    """Correlate token events with runtime events by tool_use_id or timestamp."""
    # Index runtime events by tool_use_id
    runtime_by_id = {e.get("tool_use_id"): e for e in runtime_events if e.get("tool_use_id")}

    correlated = []
    for token_event in token_events:
        tool_use_id = token_event.get("tool_use_id")

        # Try to match by tool_use_id
        runtime_event = runtime_by_id.get(tool_use_id)

        if runtime_event:
            # Merge data
            merged = {
                **token_event,
                "duration_seconds": runtime_event.get("duration_seconds"),
                "session_id": runtime_event.get("session_id"),
            }
            correlated.append(merged)
        else:
            # No runtime match - still include token data
            correlated.append(token_event)

    return correlated


def append_token_events(events: List[dict]) -> int:
    """Append token events to log file. Returns count of new events."""
    if not events:
        return 0

    path = get_token_log_path()

    # Load existing events to avoid duplicates
    existing_ids = set()
    if path.exists():
        for record in parse_jsonl_file(path):
            if record.get("tool_use_id"):
                existing_ids.add(record["tool_use_id"])

    # Append only new events
    new_count = 0
    with open(path, "a", encoding="utf-8") as f:
        for event in events:
            tool_use_id = event.get("tool_use_id")
            if tool_use_id and tool_use_id not in existing_ids:
                f.write(json.dumps(event) + "\n")
                existing_ids.add(tool_use_id)
                new_count += 1

    return new_count


def main():
    parser = argparse.ArgumentParser(description="Analyze Claude Code logs for token usage")
    parser.add_argument("--session", help="Analyze specific session only")
    parser.add_argument("--since", type=int, default=24,
                        help="Analyze logs from last N hours (default: 24)")
    parser.add_argument("--full", action="store_true",
                        help="Full analysis (ignore last analysis timestamp)")
    args = parser.parse_args()

    # Determine time range
    if args.full:
        since_time = datetime.utcnow() - timedelta(hours=args.since)
    else:
        last_analysis = get_last_analysis_time()
        if last_analysis:
            since_time = last_analysis
        else:
            since_time = datetime.utcnow() - timedelta(hours=args.since)

    print(f"[TOKEN_ANALYZER] Analyzing logs since {since_time.isoformat()}")

    # Find and parse JSONL files
    logs_dir = get_claude_logs_dir()
    print(f"[TOKEN_ANALYZER] Searching in {logs_dir}")

    all_token_events = []

    for jsonl_file in find_jsonl_files(logs_dir, since_time):
        # Filter by session if specified
        if args.session and args.session not in str(jsonl_file):
            continue

        print(f"[TOKEN_ANALYZER] Processing {jsonl_file.name}")
        records = parse_jsonl_file(jsonl_file)
        token_events = extract_task_token_usage(records)
        all_token_events.extend(token_events)

    print(f"[TOKEN_ANALYZER] Found {len(all_token_events)} Task tool invocations with token data")

    # Load runtime events for correlation
    runtime_events = load_runtime_events()
    print(f"[TOKEN_ANALYZER] Loaded {len(runtime_events)} runtime events for correlation")

    # Correlate and save
    correlated = correlate_with_runtime(all_token_events, runtime_events)
    new_count = append_token_events(correlated)

    # Update last analysis timestamp
    save_last_analysis_time()

    print(f"[TOKEN_ANALYZER] Added {new_count} new token usage records")
    print(f"[TOKEN_ANALYZER] Output: {get_token_log_path()}")


if __name__ == "__main__":
    main()
