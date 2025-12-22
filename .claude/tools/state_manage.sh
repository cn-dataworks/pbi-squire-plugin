#!/usr/bin/env bash
#
# Power BI Analyst Skill - State Manager (Bash + jq)
#
# Manages session state, tasks, and resource locks for the Power BI Analyst skill.
# Requires: bash 4+, jq
#
# Usage:
#   ./state_manage.sh summary                              Show state summary
#   ./state_manage.sh create-task "name" [workflow]        Create new task
#   ./state_manage.sh update-stage "id" "stage"            Update task stage
#   ./state_manage.sh complete "task_id"                   Mark task completed
#   ./state_manage.sh fail "task_id"                       Mark task failed
#   ./state_manage.sh archive "task_id"                    Archive task
#   ./state_manage.sh list-tasks                           List active tasks
#   ./state_manage.sh lock "path" "task_id"                Acquire lock
#   ./state_manage.sh release "path" "task_id"             Release lock
#   ./state_manage.sh force-release "path"                 Force release lock
#   ./state_manage.sh list-locks                           List all locks
#   ./state_manage.sh get-schema                           Get model schema
#   ./state_manage.sh reset                                Reset all state
#   ./state_manage.sh help                                 Show this help

set -euo pipefail

# Configuration
STATE_PATH=".claude/state.json"
TASKS_DIR=".claude/tasks"

# ============================================================
# HELPER FUNCTIONS
# ============================================================

get_iso_timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

get_unix_timestamp() {
    date +%s
}

to_safe_name() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g' | sed 's/-\+/-/g' | sed 's/^-//;s/-$//'
}

check_jq() {
    if ! command -v jq &> /dev/null; then
        echo "ERROR: jq is required but not installed." >&2
        echo "Install with: brew install jq (macOS) or apt-get install jq (Linux)" >&2
        exit 1
    fi
}

initialize_state() {
    local dir
    dir=$(dirname "$STATE_PATH")

    if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir"
    fi

    if [[ ! -f "$STATE_PATH" ]]; then
        local now
        now=$(get_iso_timestamp)
        cat > "$STATE_PATH" << EOF
{
  "session": {
    "started": "$now",
    "last_activity": "$now",
    "skill_version": "1.0.0",
    "state_backend": "bash",
    "mcp_available": false,
    "capability_probe": {
      "tested_at": "$now",
      "claude_native": false,
      "powershell": false,
      "cmd": false,
      "bash": true
    }
  },
  "model_schema": {
    "tables": [],
    "relationships": []
  },
  "active_tasks": {},
  "resource_locks": {},
  "archived_tasks": []
}
EOF
    fi
}

get_state() {
    initialize_state
    cat "$STATE_PATH"
}

save_state() {
    local state="$1"
    local now
    now=$(get_iso_timestamp)
    echo "$state" | jq ".session.last_activity = \"$now\"" > "$STATE_PATH"
}

# ============================================================
# SESSION OPERATIONS
# ============================================================

show_summary() {
    initialize_state
    local state
    state=$(get_state)

    local task_count lock_count archive_count
    task_count=$(echo "$state" | jq '.active_tasks | length')
    lock_count=$(echo "$state" | jq '.resource_locks | length')
    archive_count=$(echo "$state" | jq '.archived_tasks | length')

    jq -n \
        --arg started "$(echo "$state" | jq -r '.session.started')" \
        --arg last "$(echo "$state" | jq -r '.session.last_activity')" \
        --arg backend "$(echo "$state" | jq -r '.session.state_backend')" \
        --argjson mcp "$(echo "$state" | jq '.session.mcp_available')" \
        --argjson tasks "$task_count" \
        --argjson locks "$lock_count" \
        --argjson archived "$archive_count" \
        '{
            session_started: $started,
            last_activity: $last,
            state_backend: $backend,
            mcp_available: $mcp,
            active_task_count: $tasks,
            lock_count: $locks,
            archived_count: $archived
        }'
}

reset_state() {
    if [[ -f "$STATE_PATH" ]]; then
        rm -f "$STATE_PATH"
    fi
    echo "State reset complete"
}

# ============================================================
# TASK OPERATIONS
# ============================================================

create_task() {
    local name="$1"
    local workflow="${2:-evaluate}"

    initialize_state
    local state
    state=$(get_state)

    local sanitized timestamp task_id task_path now
    sanitized=$(to_safe_name "$name")
    timestamp=$(get_unix_timestamp)
    task_id="${sanitized}-${timestamp}"
    task_path="${TASKS_DIR}/${task_id}"
    now=$(get_iso_timestamp)

    # Create task directory
    mkdir -p "$task_path"

    # Create findings.md
    cat > "${task_path}/findings.md" << EOF
# Task Blackboard: $name

**Status:** in_progress
**Task ID:** $task_id
**Workflow:** $workflow
**Created:** $now
**Backend:** bash

---

## Section 1: Requirements
*Pending...*
EOF

    # Update state
    state=$(echo "$state" | jq \
        --arg id "$task_id" \
        --arg path "$task_path" \
        --arg workflow "$workflow" \
        --arg now "$now" \
        '.active_tasks[$id] = {
            path: $path,
            status: "in_progress",
            workflow_type: $workflow,
            created: $now,
            updated: $now,
            current_stage: "init"
        }')

    save_state "$state"
    echo "$task_id"
}

update_task_stage() {
    local task_id="$1"
    local stage="$2"

    local state
    state=$(get_state)

    if [[ $(echo "$state" | jq --arg id "$task_id" '.active_tasks[$id]') == "null" ]]; then
        echo "ERROR: Task not found: $task_id" >&2
        exit 1
    fi

    local now
    now=$(get_iso_timestamp)

    state=$(echo "$state" | jq \
        --arg id "$task_id" \
        --arg stage "$stage" \
        --arg now "$now" \
        '.active_tasks[$id].current_stage = $stage | .active_tasks[$id].updated = $now')

    save_state "$state"
    echo "OK"
}

complete_task() {
    local task_id="$1"

    local state
    state=$(get_state)

    if [[ $(echo "$state" | jq --arg id "$task_id" '.active_tasks[$id]') == "null" ]]; then
        echo "ERROR: Task not found: $task_id" >&2
        exit 1
    fi

    local now
    now=$(get_iso_timestamp)

    # Mark completed and release locks
    state=$(echo "$state" | jq \
        --arg id "$task_id" \
        --arg now "$now" \
        '.active_tasks[$id].status = "completed" |
         .active_tasks[$id].completed_at = $now |
         .resource_locks = (.resource_locks | to_entries | map(select(.value != $id)) | from_entries)')

    save_state "$state"
    echo "OK"
}

fail_task() {
    local task_id="$1"

    local state
    state=$(get_state)

    if [[ $(echo "$state" | jq --arg id "$task_id" '.active_tasks[$id]') == "null" ]]; then
        echo "ERROR: Task not found: $task_id" >&2
        exit 1
    fi

    local now
    now=$(get_iso_timestamp)

    state=$(echo "$state" | jq \
        --arg id "$task_id" \
        --arg now "$now" \
        '.active_tasks[$id].status = "failed" | .active_tasks[$id].failed_at = $now')

    save_state "$state"
    echo "OK"
}

archive_task() {
    local task_id="$1"

    local state
    state=$(get_state)

    if [[ $(echo "$state" | jq --arg id "$task_id" '.active_tasks[$id]') == "null" ]]; then
        echo "ERROR: Task not found: $task_id" >&2
        exit 1
    fi

    local now
    now=$(get_iso_timestamp)

    # Add to archive, remove from active, release locks
    state=$(echo "$state" | jq \
        --arg id "$task_id" \
        --arg now "$now" \
        '.archived_tasks += [{
            task_id: $id,
            workflow_type: .active_tasks[$id].workflow_type,
            completed_at: (.active_tasks[$id].completed_at // $now),
            status: .active_tasks[$id].status
        }] |
        del(.active_tasks[$id]) |
        .resource_locks = (.resource_locks | to_entries | map(select(.value != $id)) | from_entries)')

    save_state "$state"
    echo "OK"
}

list_tasks() {
    initialize_state
    local state
    state=$(get_state)
    echo "$state" | jq '.active_tasks'
}

# ============================================================
# LOCK OPERATIONS
# ============================================================

acquire_lock() {
    local resource="$1"
    local task_id="$2"

    initialize_state
    local state
    state=$(get_state)

    local owner
    owner=$(echo "$state" | jq -r --arg res "$resource" '.resource_locks[$res] // empty')

    if [[ -n "$owner" && "$owner" != "$task_id" ]]; then
        echo "LOCKED:$owner"
        exit 1
    fi

    state=$(echo "$state" | jq \
        --arg res "$resource" \
        --arg id "$task_id" \
        '.resource_locks[$res] = $id')

    save_state "$state"
    echo "OK"
}

release_lock() {
    local resource="$1"
    local task_id="$2"

    local state
    state=$(get_state)

    local owner
    owner=$(echo "$state" | jq -r --arg res "$resource" '.resource_locks[$res] // empty')

    if [[ -z "$owner" ]]; then
        echo "OK"
        return
    fi

    if [[ "$owner" != "$task_id" ]]; then
        echo "ERROR: Cannot release lock owned by: $owner" >&2
        exit 1
    fi

    state=$(echo "$state" | jq --arg res "$resource" 'del(.resource_locks[$res])')

    save_state "$state"
    echo "OK"
}

force_release_lock() {
    local resource="$1"

    local state
    state=$(get_state)

    state=$(echo "$state" | jq --arg res "$resource" 'del(.resource_locks[$res])')

    save_state "$state"
    echo "OK"
}

list_locks() {
    initialize_state
    local state
    state=$(get_state)
    echo "$state" | jq '.resource_locks'
}

# ============================================================
# SCHEMA OPERATIONS
# ============================================================

get_model_schema() {
    initialize_state
    local state
    state=$(get_state)
    echo "$state" | jq '.model_schema'
}

# ============================================================
# HELP
# ============================================================

show_help() {
    cat << 'EOF'
Power BI Analyst Skill - State Manager (Bash + jq)

USAGE:
    state_manage.sh summary                              Show state summary
    state_manage.sh create-task "name" [workflow]        Create new task
    state_manage.sh update-stage "id" "stage"            Update task stage
    state_manage.sh complete "task_id"                   Mark task completed
    state_manage.sh fail "task_id"                       Mark task failed
    state_manage.sh archive "task_id"                    Archive task
    state_manage.sh list-tasks                           List active tasks
    state_manage.sh lock "path" "task_id"                Acquire lock
    state_manage.sh release "path" "task_id"             Release lock
    state_manage.sh force-release "path"                 Force release lock
    state_manage.sh list-locks                           List all locks
    state_manage.sh get-schema                           Get model schema
    state_manage.sh reset                                Reset all state
    state_manage.sh help                                 Show this help

WORKFLOWS:
    evaluate    - Analyze existing code issues
    create      - Create new artifacts
    implement   - Apply planned changes
    analyze     - Dashboard analysis
    merge       - Merge projects

EXAMPLES:
    ./state_manage.sh create-task "fix-yoy-calc" evaluate
    ./state_manage.sh lock "definition/tables/Sales.tmdl" "fix-yoy-calc-1734872400"
    ./state_manage.sh complete "fix-yoy-calc-1734872400"
EOF
}

# ============================================================
# MAIN
# ============================================================

check_jq

case "${1:-help}" in
    summary)
        show_summary
        ;;
    reset)
        reset_state
        ;;
    create-task)
        create_task "${2:-unnamed}" "${3:-evaluate}"
        ;;
    update-stage)
        update_task_stage "$2" "$3"
        ;;
    complete)
        complete_task "$2"
        ;;
    fail)
        fail_task "$2"
        ;;
    archive)
        archive_task "$2"
        ;;
    list-tasks)
        list_tasks
        ;;
    lock)
        acquire_lock "$2" "$3"
        ;;
    release)
        release_lock "$2" "$3"
        ;;
    force-release)
        force_release_lock "$2"
        ;;
    list-locks)
        list_locks
        ;;
    get-schema)
        get_model_schema
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $1" >&2
        show_help
        exit 1
        ;;
esac
