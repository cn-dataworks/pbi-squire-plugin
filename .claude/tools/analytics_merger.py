#!/usr/bin/env python3
"""
Analytics Merger - Combine runtime and token data into aggregated analytics.

This script merges runtime_events.jsonl and token_usage.jsonl to produce
comprehensive agent analytics with aggregations by agent, command, and time.

Usage:
    python analytics_merger.py [--output FILE]

Options:
    --output    Output file path (default: agent_scratchpads/_analytics/agent_analytics.json)
"""

import json
import sys
import os
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


def get_analytics_dir() -> Path:
    """Get analytics directory, respecting environment variable override."""
    env_path = os.environ.get("POWERBI_ANALYST_ANALYTICS_PATH")
    if env_path:
        return Path(env_path)
    return Path("agent_scratchpads/_analytics")


def parse_jsonl_file(file_path: Path) -> List[dict]:
    """Parse a JSONL file and return list of records."""
    records = []
    if not file_path.exists():
        return records

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except IOError:
        pass

    return records


def merge_events(runtime_events: List[dict], token_events: List[dict]) -> List[dict]:
    """Merge runtime and token events by tool_use_id."""
    # Index token events by tool_use_id
    token_by_id = {}
    for event in token_events:
        tool_use_id = event.get("tool_use_id")
        if tool_use_id:
            token_by_id[tool_use_id] = event

    merged = []

    # Start with runtime events and enrich with token data
    for runtime in runtime_events:
        tool_use_id = runtime.get("tool_use_id")
        token_data = token_by_id.get(tool_use_id, {})

        merged_event = {
            **runtime,
            "input_tokens": token_data.get("input_tokens"),
            "output_tokens": token_data.get("output_tokens"),
            "total_tokens": token_data.get("total_tokens"),
        }
        merged.append(merged_event)

    # Add any token events without matching runtime events
    runtime_ids = {e.get("tool_use_id") for e in runtime_events}
    for token in token_events:
        tool_use_id = token.get("tool_use_id")
        if tool_use_id and tool_use_id not in runtime_ids:
            merged.append(token)

    return merged


def calculate_aggregations(events: List[dict]) -> dict:
    """Calculate aggregated statistics from merged events."""

    # Initialize aggregation structures
    by_agent = defaultdict(lambda: {
        "invocations": 0,
        "total_duration_seconds": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_tokens": 0,
        "durations": [],
        "token_counts": [],
    })

    by_session = defaultdict(lambda: {
        "agents_used": set(),
        "total_duration_seconds": 0,
        "total_tokens": 0,
        "invocations": 0,
    })

    by_date = defaultdict(lambda: {
        "invocations": 0,
        "total_duration_seconds": 0,
        "total_tokens": 0,
        "agents_used": set(),
    })

    # Process events
    for event in events:
        agent_name = event.get("agent_name", "unknown")
        session_id = event.get("session_id", "unknown")
        duration = event.get("duration_seconds") or 0
        input_tokens = event.get("input_tokens") or 0
        output_tokens = event.get("output_tokens") or 0
        total_tokens = event.get("total_tokens") or (input_tokens + output_tokens)

        # Parse timestamp for date grouping
        timestamp = event.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.rstrip("Z"))
                date_key = dt.strftime("%Y-%m-%d")
            except ValueError:
                date_key = "unknown"
        else:
            date_key = "unknown"

        # By agent
        by_agent[agent_name]["invocations"] += 1
        by_agent[agent_name]["total_duration_seconds"] += duration
        by_agent[agent_name]["total_input_tokens"] += input_tokens
        by_agent[agent_name]["total_output_tokens"] += output_tokens
        by_agent[agent_name]["total_tokens"] += total_tokens
        if duration > 0:
            by_agent[agent_name]["durations"].append(duration)
        if total_tokens > 0:
            by_agent[agent_name]["token_counts"].append(total_tokens)

        # By session
        by_session[session_id]["agents_used"].add(agent_name)
        by_session[session_id]["total_duration_seconds"] += duration
        by_session[session_id]["total_tokens"] += total_tokens
        by_session[session_id]["invocations"] += 1

        # By date
        by_date[date_key]["invocations"] += 1
        by_date[date_key]["total_duration_seconds"] += duration
        by_date[date_key]["total_tokens"] += total_tokens
        by_date[date_key]["agents_used"].add(agent_name)

    # Calculate summary statistics
    total_invocations = len(events)
    total_duration = sum(e.get("duration_seconds") or 0 for e in events)
    total_tokens = sum(e.get("total_tokens") or 0 for e in events)

    # Finalize by_agent with averages
    agent_stats = {}
    for agent_name, data in by_agent.items():
        agent_stats[agent_name] = {
            "invocations": data["invocations"],
            "total_duration_seconds": round(data["total_duration_seconds"], 2),
            "avg_duration_seconds": (
                round(data["total_duration_seconds"] / data["invocations"], 2)
                if data["invocations"] > 0 else 0
            ),
            "total_tokens": data["total_tokens"],
            "total_input_tokens": data["total_input_tokens"],
            "total_output_tokens": data["total_output_tokens"],
            "avg_tokens": (
                round(data["total_tokens"] / data["invocations"])
                if data["invocations"] > 0 else 0
            ),
        }

    # Finalize by_session (convert sets to lists)
    session_stats = {}
    for session_id, data in by_session.items():
        session_stats[session_id] = {
            "agents_used": sorted(list(data["agents_used"])),
            "total_duration_seconds": round(data["total_duration_seconds"], 2),
            "total_tokens": data["total_tokens"],
            "invocations": data["invocations"],
        }

    # Finalize by_date (convert sets to lists)
    date_stats = {}
    for date_key, data in sorted(by_date.items(), reverse=True):
        date_stats[date_key] = {
            "invocations": data["invocations"],
            "total_duration_seconds": round(data["total_duration_seconds"], 2),
            "total_tokens": data["total_tokens"],
            "agents_used": sorted(list(data["agents_used"])),
        }

    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "summary": {
            "total_invocations": total_invocations,
            "total_sessions": len(by_session),
            "total_duration_seconds": round(total_duration, 2),
            "total_tokens": total_tokens,
            "unique_agents": len(by_agent),
        },
        "by_agent": dict(sorted(agent_stats.items(), key=lambda x: x[1]["invocations"], reverse=True)),
        "by_session": session_stats,
        "by_date": date_stats,
    }


def save_analytics(analytics: dict, output_path: Path) -> None:
    """Save analytics to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analytics, f, indent=2)


def print_summary(analytics: dict) -> None:
    """Print a human-readable summary to stdout."""
    summary = analytics.get("summary", {})

    print("\n" + "=" * 60)
    print("AGENT ANALYTICS SUMMARY")
    print("=" * 60)
    print(f"Generated: {analytics.get('generated_at', 'N/A')}")
    print(f"\nTotal invocations: {summary.get('total_invocations', 0)}")
    print(f"Total sessions: {summary.get('total_sessions', 0)}")
    print(f"Total runtime: {summary.get('total_duration_seconds', 0):.1f} seconds")
    print(f"Total tokens: {summary.get('total_tokens', 0):,}")
    print(f"Unique agents: {summary.get('unique_agents', 0)}")

    print("\n" + "-" * 60)
    print("TOP AGENTS BY INVOCATIONS")
    print("-" * 60)

    by_agent = analytics.get("by_agent", {})
    for i, (agent_name, stats) in enumerate(list(by_agent.items())[:10]):
        print(f"\n{i+1}. {agent_name}")
        print(f"   Invocations: {stats['invocations']}")
        print(f"   Avg duration: {stats['avg_duration_seconds']:.1f}s")
        print(f"   Avg tokens: {stats['avg_tokens']:,}")
        print(f"   Total tokens: {stats['total_tokens']:,}")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Merge runtime and token data into analytics")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress summary output")
    args = parser.parse_args()

    analytics_dir = get_analytics_dir()

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = analytics_dir / "agent_analytics.json"

    # Load event logs
    runtime_path = analytics_dir / "runtime_events.jsonl"
    token_path = analytics_dir / "token_usage.jsonl"

    print(f"[ANALYTICS_MERGER] Loading runtime events from {runtime_path}")
    runtime_events = parse_jsonl_file(runtime_path)
    print(f"[ANALYTICS_MERGER] Loaded {len(runtime_events)} runtime events")

    print(f"[ANALYTICS_MERGER] Loading token events from {token_path}")
    token_events = parse_jsonl_file(token_path)
    print(f"[ANALYTICS_MERGER] Loaded {len(token_events)} token events")

    # Merge events
    merged_events = merge_events(runtime_events, token_events)
    print(f"[ANALYTICS_MERGER] Merged into {len(merged_events)} events")

    # Calculate aggregations
    analytics = calculate_aggregations(merged_events)

    # Save to file
    save_analytics(analytics, output_path)
    print(f"[ANALYTICS_MERGER] Saved analytics to {output_path}")

    # Print summary unless quiet mode
    if not args.quiet:
        print_summary(analytics)


if __name__ == "__main__":
    main()
