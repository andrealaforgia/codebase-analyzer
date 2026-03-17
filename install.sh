#!/usr/bin/env bash

# alf-codebase-analyzer Installer
# Installs the orchestrator agent and global command for Claude Code

set -e

# Colors for output
if [[ -t 1 ]] && [[ -z "$NO_COLOR" ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_AGENTS_DIR="$HOME/.claude/agents"
CLAUDE_COMMANDS_DIR="$HOME/.claude/commands"

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     alf-codebase-analyzer Installer            ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  install       Install the agent and commands (default)"
    echo "  uninstall     Remove the agent and commands"
    echo "  status        Show installation status"
    echo ""
    echo "Options:"
    echo "  -f, --force   Overwrite existing files without prompting"
    echo "  -h, --help    Show this help message"
    echo ""
}

check_status() {
    echo -e "${YELLOW}Installation status:${NC}"
    echo ""

    local agent_path="$CLAUDE_AGENTS_DIR/alf-codebase-analyzer.md"
    if [[ -f "$agent_path" ]]; then
        echo -e "  ${GREEN}✓${NC} Agent definition installed at $agent_path"
    else
        echo -e "  ${RED}✗${NC} Agent definition not installed"
    fi

    local commands=("alf-analyze" "alf-slt-report" "alf-summary-report")
    for cmd in "${commands[@]}"; do
        local cmd_path="$CLAUDE_COMMANDS_DIR/${cmd}.md"
        if [[ -f "$cmd_path" ]]; then
            echo -e "  ${GREEN}✓${NC} /${cmd} command installed at $cmd_path"
        else
            echo -e "  ${RED}✗${NC} /${cmd} command not installed"
        fi
    done
    echo ""
}

install_file() {
    local source="$1"
    local target="$2"
    local label="$3"
    local force="$4"

    if [[ ! -f "$source" ]]; then
        echo -e "  ${RED}✗${NC} Source not found: $source"
        return 1
    fi

    if [[ -f "$target" && "$force" != "true" ]]; then
        echo -ne "  ${YELLOW}$label${NC} already exists. Overwrite? [y/N] "
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo -e "  ${YELLOW}Skipped${NC} $label"
            return 0
        fi
    fi

    mkdir -p "$(dirname "$target")"
    # Replace {{ANALYZER_HOME}} placeholder with the actual project path
    # so the Python pipeline can be invoked from any working directory
    sed "s|{{ANALYZER_HOME}}|$SCRIPT_DIR|g" "$source" > "$target"
    echo -e "  ${GREEN}✓${NC} Installed $label"
}

do_install() {
    local force="$1"
    echo -e "${YELLOW}Installing alf-codebase-analyzer...${NC}"
    echo ""

    # Install agent definition to ~/.claude/agents/
    install_file \
        "$SCRIPT_DIR/alf-codebase-analyzer.md" \
        "$CLAUDE_AGENTS_DIR/alf-codebase-analyzer.md" \
        "agent definition" \
        "$force"

    # Install commands to ~/.claude/commands/
    install_file \
        "$SCRIPT_DIR/alf-codebase-analyzer.md" \
        "$CLAUDE_COMMANDS_DIR/alf-analyze.md" \
        "/alf-analyze command" \
        "$force"

    install_file \
        "$SCRIPT_DIR/commands/alf-slt-report.md" \
        "$CLAUDE_COMMANDS_DIR/alf-slt-report.md" \
        "/alf-slt-report command" \
        "$force"

    install_file \
        "$SCRIPT_DIR/commands/alf-summary-report.md" \
        "$CLAUDE_COMMANDS_DIR/alf-summary-report.md" \
        "/alf-summary-report command" \
        "$force"

    echo ""
    echo -e "${GREEN}Installation complete!${NC}"
    echo ""
    echo "The agent is now available in Claude Code as:"
    echo -e "  ${BLUE}alf-codebase-analyzer${NC}  (via Agent tool)"
    echo -e "  ${BLUE}/alf-analyze${NC}           (via slash command)"
    echo -e "  ${BLUE}/alf-slt-report${NC}        (via slash command)"
    echo -e "  ${BLUE}/alf-summary-report${NC}    (via slash command)"
    echo ""
    echo "Restart Claude Code or start a new session to use the agent."
    echo ""
}

do_uninstall() {
    echo -e "${YELLOW}Removing alf-codebase-analyzer...${NC}"
    echo ""

    local agent_path="$CLAUDE_AGENTS_DIR/alf-codebase-analyzer.md"
    if [[ -f "$agent_path" ]]; then
        rm "$agent_path"
        echo -e "  ${GREEN}✓${NC} Removed agent definition"
    else
        echo -e "  ${YELLOW}!${NC} Agent definition was not installed"
    fi

    local commands=("alf-analyze" "alf-slt-report" "alf-summary-report")
    for cmd in "${commands[@]}"; do
        local cmd_path="$CLAUDE_COMMANDS_DIR/${cmd}.md"
        if [[ -f "$cmd_path" ]]; then
            rm "$cmd_path"
            echo -e "  ${GREEN}✓${NC} Removed /${cmd} command"
        else
            echo -e "  ${YELLOW}!${NC} /${cmd} command was not installed"
        fi
    done

    echo ""
    echo -e "${GREEN}Uninstallation complete!${NC}"
    echo ""
}

main() {
    local command="install"
    local force="false"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -f|--force)
                force="true"
                shift
                ;;
            -h|--help)
                print_header
                print_usage
                exit 0
                ;;
            install|uninstall|status)
                command="$1"
                shift
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                print_usage
                exit 1
                ;;
        esac
    done

    print_header

    case "$command" in
        install)
            do_install "$force"
            ;;
        uninstall)
            echo -ne "${YELLOW}Remove alf-codebase-analyzer? [y/N] ${NC}"
            read -r response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                do_uninstall
            else
                echo "Cancelled."
            fi
            ;;
        status)
            check_status
            ;;
    esac
}

main "$@"
