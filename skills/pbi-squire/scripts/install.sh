#!/usr/bin/env bash
#
# PBI Squire Skill - Installer (Bash)
#
# Sets up the PBI Squire skill for Claude Code:
# - Detects MCP binary availability
# - Configures Claude settings if MCP found
# - Initializes state management
# - Reports configuration status
#
# Usage:
#   ./install.sh
#   ./install.sh --skip-mcp-config
#   ./install.sh --verbose

set -euo pipefail

# ============================================================
# CONFIGURATION
# ============================================================

SKILL_NAME="pbi-squire"
SKILL_VERSION="1.0.0"
MCP_BINARY_NAME="powerbi-modeling-mcp"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_MANAGER_PATH="$SCRIPT_DIR/../../tools/state_manage.sh"

SKIP_MCP_CONFIG=false
FORCE=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-mcp-config) SKIP_MCP_CONFIG=true; shift ;;
        --force) FORCE=true; shift ;;
        --verbose|-v) VERBOSE=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# ============================================================
# HELPER FUNCTIONS
# ============================================================

write_step() {
    echo -e "\n\033[36m[$SKILL_NAME]\033[0m $1"
}

write_success() {
    echo -e "  \033[32m[OK]\033[0m $1"
}

write_warning() {
    echo -e "  \033[33m[!]\033[0m $1"
}

write_error() {
    echo -e "  \033[31m[X]\033[0m $1"
}

write_info() {
    echo -e "      \033[90m$1\033[0m"
}

# ============================================================
# PREREQUISITE CHECKS
# ============================================================

check_prerequisites() {
    write_step "Checking prerequisites..."

    local all_passed=true

    # Check bash version
    if [[ ${BASH_VERSION%%.*} -ge 4 ]]; then
        write_success "Bash ${BASH_VERSION} - OK"
    else
        write_warning "Bash 4+ recommended (found ${BASH_VERSION})"
    fi

    # Check jq for JSON manipulation
    if command -v jq &> /dev/null; then
        write_success "jq found - OK"
    else
        write_warning "jq not found - some features may not work"
        write_info "Install with: brew install jq (macOS) or apt-get install jq (Linux)"
    fi

    # Check if running from skill directory
    if [[ -f "$SCRIPT_DIR/SKILL.md" ]]; then
        write_success "Running from skill directory"
    else
        write_warning "Not running from skill directory"
    fi

    # Check state manager
    if [[ -f "$STATE_MANAGER_PATH" ]]; then
        write_success "State manager found"
    else
        write_warning "State manager not found at $STATE_MANAGER_PATH"
    fi

    echo "$all_passed"
}

# ============================================================
# MCP DETECTION
# ============================================================

find_mcp_binary() {
    write_step "Searching for Power BI Modeling MCP..."

    # Check PATH first
    if command -v "$MCP_BINARY_NAME" &> /dev/null; then
        local path
        path=$(command -v "$MCP_BINARY_NAME")
        write_success "Found in PATH: $path"
        echo "$path"
        return 0
    fi

    # Search common locations (macOS/Linux)
    local search_paths=(
        "$HOME/.vscode/extensions/*/$MCP_BINARY_NAME"
        "$HOME/.vscode-insiders/extensions/*/$MCP_BINARY_NAME"
        "/usr/local/bin/$MCP_BINARY_NAME"
        "/opt/powerbi-mcp/$MCP_BINARY_NAME"
        "$HOME/.local/bin/$MCP_BINARY_NAME"
        "$HOME/bin/$MCP_BINARY_NAME"
    )

    for pattern in "${search_paths[@]}"; do
        # shellcheck disable=SC2086
        for match in $pattern; do
            if [[ -f "$match" ]]; then
                write_success "Found: $match"
                echo "$match"
                return 0
            fi
        done
    done

    write_warning "MCP binary not found"
    write_info "The skill will run in File-Only mode (limited validation)"
    write_info "To enable full features, install Power BI Modeling MCP from:"
    write_info "https://github.com/microsoft/powerbi-modeling-mcp"
    echo ""
    return 1
}

# ============================================================
# CLAUDE CONFIGURATION
# ============================================================

get_claude_config_path() {
    local paths=(
        "$HOME/Library/Application Support/Claude/claude_desktop_config.json"  # macOS
        "$HOME/.config/claude/claude_desktop_config.json"                       # Linux
        "$HOME/.claude/settings.json"                                           # Generic
    )

    for path in "${paths[@]}"; do
        if [[ -f "$path" ]]; then
            echo "$path"
            return 0
        fi
    done

    # Return default based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
    else
        echo "$HOME/.config/claude/claude_desktop_config.json"
    fi
}

update_claude_config() {
    local mcp_path="$1"

    if [[ "$SKIP_MCP_CONFIG" == "true" ]]; then
        write_info "Skipping Claude config update (--skip-mcp-config)"
        return
    fi

    if ! command -v jq &> /dev/null; then
        write_warning "jq not installed - cannot update Claude config automatically"
        write_info "Manual configuration required. Add to your Claude config:"
        write_info '  "mcpServers": { "powerbi-modeling": { "command": "'$mcp_path'" } }'
        return
    fi

    write_step "Configuring Claude for MCP..."

    local config_path
    config_path=$(get_claude_config_path)
    local config_dir
    config_dir=$(dirname "$config_path")

    # Create directory if needed
    if [[ ! -d "$config_dir" ]]; then
        mkdir -p "$config_dir"
        write_info "Created $config_dir"
    fi

    # Load or create config
    local config
    if [[ -f "$config_path" ]]; then
        config=$(cat "$config_path")
        write_info "Updating existing config: $config_path"

        # Check if already configured
        local existing
        existing=$(echo "$config" | jq -r '.mcpServers."powerbi-modeling".command // empty')
        if [[ -n "$existing" && "$FORCE" != "true" ]]; then
            if [[ "$existing" == "$mcp_path" ]]; then
                write_success "MCP already configured correctly"
                return
            fi
            write_warning "MCP already configured with different path"
            write_info "Existing: $existing"
            write_info "New:      $mcp_path"
            write_info "Use --force to overwrite"
            return
        fi
    else
        config='{}'
        write_info "Creating new config: $config_path"
    fi

    # Update config with MCP server
    config=$(echo "$config" | jq --arg cmd "$mcp_path" '
        .mcpServers = (.mcpServers // {}) |
        .mcpServers."powerbi-modeling" = {
            "command": $cmd,
            "args": [],
            "env": {}
        }
    ')

    # Save config
    echo "$config" > "$config_path"
    write_success "Claude config updated: $config_path"
}

# ============================================================
# STATE INITIALIZATION
# ============================================================

initialize_skill_state() {
    write_step "Initializing skill state..."

    local state_dir=".claude"
    local state_path="$state_dir/state.json"

    # Create .claude directory if needed
    if [[ ! -d "$state_dir" ]]; then
        mkdir -p "$state_dir"
        write_info "Created $state_dir directory"
    fi

    # Initialize via state manager if available
    if [[ -f "$STATE_MANAGER_PATH" && -x "$STATE_MANAGER_PATH" ]]; then
        if "$STATE_MANAGER_PATH" summary &> /dev/null; then
            write_success "State initialized"
            return
        fi
    fi

    # Manual initialization
    if [[ ! -f "$state_path" ]]; then
        local now
        now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        cat > "$state_path" << EOF
{
  "session": {
    "started": "$now",
    "last_activity": "$now",
    "skill_version": "$SKILL_VERSION",
    "state_backend": "bash",
    "mcp_available": false
  },
  "active_tasks": {},
  "resource_locks": {},
  "archived_tasks": []
}
EOF
        write_success "State file created"
    else
        write_success "State file exists"
    fi
}

# ============================================================
# SUMMARY REPORT
# ============================================================

show_install_summary() {
    local mcp_available="$1"
    local mcp_path="${2:-}"

    echo ""
    echo -e "\033[36m============================================================\033[0m"
    echo -e "\033[36m PBI Squire Skill - Installation Complete\033[0m"
    echo -e "\033[36m============================================================\033[0m"

    echo ""
    echo -e "\033[37m Configuration:\033[0m"
    echo "   Skill Version:  $SKILL_VERSION"
    echo "   State Backend:  Bash"

    if [[ "$mcp_available" == "true" ]]; then
        echo -n "   MCP Status:     "
        echo -e "\033[32mENABLED\033[0m"
        echo "   MCP Path:       $mcp_path"
        echo ""
        echo "   Mode:           Desktop Mode (full validation)"
    else
        echo -n "   MCP Status:     "
        echo -e "\033[33mNOT FOUND\033[0m"
        echo ""
        echo "   Mode:           File-Only Mode (limited validation)"
        echo "   To enable full features, install Power BI Modeling MCP"
    fi

    echo ""
    echo -e "\033[37m Getting Started:\033[0m"
    echo "   1. Open a Power BI project (.pbip folder)"
    echo "   2. Ask Claude: 'Help me analyze this Power BI project'"
    echo "   3. Or use a workflow: /evaluate-pbi-project-file"

    echo ""
    echo -e "\033[37m Documentation:\033[0m"
    echo "   - Getting Started:  references/getting-started.md"
    echo "   - Glossary:         references/glossary.md"
    echo "   - Troubleshooting:  references/troubleshooting-faq.md"

    echo ""
    echo -e "\033[36m============================================================\033[0m"
}

# ============================================================
# MAIN
# ============================================================

main() {
    echo ""
    echo -e "\033[36mPBI Squire Skill Installer\033[0m"
    echo -e "\033[90mVersion $SKILL_VERSION\033[0m"
    echo ""

    # Check prerequisites
    check_prerequisites

    # Find MCP binary
    local mcp_path
    local mcp_available="false"
    if mcp_path=$(find_mcp_binary); then
        mcp_available="true"
    fi

    # Configure Claude if MCP found
    if [[ "$mcp_available" == "true" && -n "$mcp_path" ]]; then
        update_claude_config "$mcp_path"
    fi

    # Initialize state
    initialize_skill_state

    # Update state with MCP status
    local state_path=".claude/state.json"
    if [[ -f "$state_path" ]] && command -v jq &> /dev/null; then
        jq --argjson mcp "$mcp_available" '.session.mcp_available = $mcp' "$state_path" > "$state_path.tmp"
        mv "$state_path.tmp" "$state_path"
    fi

    # Show summary
    show_install_summary "$mcp_available" "$mcp_path"
}

main "$@"
