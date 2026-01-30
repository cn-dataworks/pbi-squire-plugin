#!/usr/bin/env bash
#
# Bootstrap script for PBI Squire Plugin - copies tools to project directory.
#
# This script ensures the user's project has the necessary tools and helpers
# from the plugin. It:
# - Checks if local tools exist
# - Compares versions
# - Copies/updates tools as needed
# - Creates the .claude directory structure
#
# Usage:
#   ./bootstrap.sh           Run bootstrap
#   ./bootstrap.sh --force   Force update even if versions match
#   ./bootstrap.sh --check   Only check if update is needed
#   ./bootstrap.sh --silent  Suppress output messages

set -euo pipefail

# ============================================================
# CONFIGURATION
# ============================================================

# Determine plugin path (this script is in {plugin}/tools/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_PATH="$(dirname "$SCRIPT_DIR")"

# Check if we're in the right place
if [[ ! -d "$PLUGIN_PATH/.claude-plugin" ]]; then
    # Might be nested differently
    PLUGIN_PATH="$(dirname "$PLUGIN_PATH")"
fi

PLUGIN_TOOLS_PATH="$PLUGIN_PATH/tools"
DEVELOPER_TOOLS_PATH="$PLUGIN_TOOLS_PATH/developer"
PLUGIN_RESOURCES_PATH="$PLUGIN_PATH/skills/pbi-squire/resources"
VERSION_FILE="version.txt"

# Local paths (in user's project)
LOCAL_CLAUDE_DIR=".claude"
LOCAL_TOOLS_DIR=".claude/tools/pbi-squire"
LOCAL_HELPERS_DIR=".claude/helpers/pbi-squire"

# Files to copy
TOOL_FILES=(
    "token_analyzer.py"
    "analytics_merger.py"
    "tmdl_format_validator.py"
    "tmdl_measure_replacer.py"
    "pbir_visual_editor.py"
    "pbi_project_validator.py"
    "pbi_merger_utils.py"
    "pbi_merger_schemas.json"
    "extract_visual_layout.py"
    "agent_logger.py"
    "version.txt"
)

HELPER_FILES=(
    "pbi-url-filter-encoder.md"
)

# Flags
FORCE=false
SILENT=false
CHECK_ONLY=false

# ============================================================
# ARGUMENT PARSING
# ============================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --force|-f)
            FORCE=true
            shift
            ;;
        --silent|-s)
            SILENT=true
            shift
            ;;
        --check|-c)
            CHECK_ONLY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# ============================================================
# HELPER FUNCTIONS
# ============================================================

write_info() {
    if [[ "$SILENT" != "true" ]]; then
        echo -e "  [bootstrap] $1"
    fi
}

write_success() {
    if [[ "$SILENT" != "true" ]]; then
        echo -e "  [bootstrap] \033[32m$1\033[0m"
    fi
}

write_warn() {
    if [[ "$SILENT" != "true" ]]; then
        echo -e "  [bootstrap] \033[33m$1\033[0m"
    fi
}

write_error() {
    echo -e "  [bootstrap] \033[31mERROR: $1\033[0m" >&2
}

# ============================================================
# VERSION FUNCTIONS
# ============================================================

get_plugin_version() {
    local version_path="$DEVELOPER_TOOLS_PATH/$VERSION_FILE"
    if [[ -f "$version_path" ]]; then
        cat "$version_path" | tr -d '[:space:]'
    else
        echo "0.0.0"
    fi
}

get_local_version() {
    local version_path="$LOCAL_TOOLS_DIR/$VERSION_FILE"
    if [[ -f "$version_path" ]]; then
        cat "$version_path" | tr -d '[:space:]'
    else
        echo ""
    fi
}

# Compare two version strings
# Returns: "missing", "outdated", "newer", or "current"
compare_versions() {
    local plugin_version="$1"
    local local_version="$2"

    if [[ -z "$local_version" ]]; then
        echo "missing"
        return
    fi

    # Split versions into arrays
    IFS='.' read -ra PLUGIN_PARTS <<< "$plugin_version"
    IFS='.' read -ra LOCAL_PARTS <<< "$local_version"

    for i in 0 1 2; do
        local p="${PLUGIN_PARTS[$i]:-0}"
        local l="${LOCAL_PARTS[$i]:-0}"

        if (( p > l )); then
            echo "outdated"
            return
        fi
        if (( p < l )); then
            echo "newer"
            return
        fi
    done

    echo "current"
}

# ============================================================
# COPY FUNCTIONS
# ============================================================

initialize_local_directories() {
    if [[ ! -d "$LOCAL_CLAUDE_DIR" ]]; then
        mkdir -p "$LOCAL_CLAUDE_DIR"
        write_info "Created $LOCAL_CLAUDE_DIR directory"
    fi

    if [[ ! -d "$LOCAL_TOOLS_DIR" ]]; then
        mkdir -p "$LOCAL_TOOLS_DIR"
        write_info "Created $LOCAL_TOOLS_DIR directory"
    fi

    if [[ ! -d "$LOCAL_HELPERS_DIR" ]]; then
        mkdir -p "$LOCAL_HELPERS_DIR"
        write_info "Created $LOCAL_HELPERS_DIR directory"
    fi

    # Create tasks directory for workflow outputs
    local tasks_dir="$LOCAL_CLAUDE_DIR/tasks"
    if [[ ! -d "$tasks_dir" ]]; then
        mkdir -p "$tasks_dir"
        write_info "Created $tasks_dir directory"
    fi
}

copy_tool_files() {
    local copied=0
    local skipped=0

    for file in "${TOOL_FILES[@]}"; do
        local source_path="$DEVELOPER_TOOLS_PATH/$file"
        local dest_path="$LOCAL_TOOLS_DIR/$file"

        if [[ -f "$source_path" ]]; then
            cp "$source_path" "$dest_path"
            ((copied++))
        else
            write_warn "Tool file not found: $file"
            ((skipped++))
        fi
    done

    write_info "Copied $copied tool files"
    if (( skipped > 0 )); then
        write_warn "Skipped $skipped missing files"
    fi
}

copy_helper_files() {
    local copied=0

    for file in "${HELPER_FILES[@]}"; do
        local source_path="$PLUGIN_RESOURCES_PATH/$file"
        local dest_path="$LOCAL_HELPERS_DIR/$file"

        if [[ -f "$source_path" ]]; then
            cp "$source_path" "$dest_path"
            ((copied++))
        else
            write_warn "Helper file not found: $file"
        fi
    done

    write_info "Copied $copied helper files"
}

copy_docs_files() {
    local docs_source="$PLUGIN_TOOLS_PATH/docs"
    local docs_dir="$LOCAL_TOOLS_DIR/docs"

    if [[ -d "$docs_source" ]]; then
        mkdir -p "$docs_dir"
        cp -r "$docs_source"/* "$docs_dir/"
        write_info "Copied documentation files"
    fi
}

# ============================================================
# MAIN
# ============================================================

main() {
    local plugin_version
    local local_version
    local status

    plugin_version=$(get_plugin_version)
    local_version=$(get_local_version)
    status=$(compare_versions "$plugin_version" "$local_version")

    # Detect edition (Developer vs Analyst)
    local dev_features_path="$PLUGIN_PATH/skills/pbi-squire/developer-features.md"
    local edition="Analyst"
    if [[ -f "$dev_features_path" ]]; then
        edition="Developer"
    fi

    write_info "Plugin version: $plugin_version ($edition Edition)"
    write_info "Local version:  ${local_version:-(not installed)}"
    write_info "Status: $status"

    # Determine if we need to copy
    local needs_copy=false

    case $status in
        "missing")
            write_info "Tools not found in project - will install"
            needs_copy=true
            ;;
        "outdated")
            write_warn "Local tools are outdated - will update"
            needs_copy=true
            ;;
        "newer")
            write_warn "Local tools are newer than plugin (manual edits?)"
            if [[ "$FORCE" == "true" ]]; then
                write_info "Force flag set - will overwrite"
                needs_copy=true
            fi
            ;;
        "current")
            write_success "Tools are up to date"
            if [[ "$FORCE" == "true" ]]; then
                write_info "Force flag set - will refresh"
                needs_copy=true
            fi
            ;;
    esac

    # Check-only mode
    if [[ "$CHECK_ONLY" == "true" ]]; then
        if [[ "$needs_copy" == "true" ]]; then
            write_info "Update available: $local_version -> $plugin_version"
            exit 1  # Exit code 1 = update needed
        else
            write_success "No update needed"
            exit 0  # Exit code 0 = current
        fi
    fi

    # Perform copy if needed
    if [[ "$needs_copy" == "true" ]]; then
        initialize_local_directories
        copy_tool_files
        copy_helper_files
        copy_docs_files

        write_success "Bootstrap complete! Tools installed to $LOCAL_TOOLS_DIR"
        write_info "Version: $plugin_version"
    fi

    exit 0
}

main
