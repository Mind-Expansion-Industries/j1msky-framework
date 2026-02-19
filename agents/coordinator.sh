#!/bin/bash
# J1MSKY Agent Coordinator
# Start, stop, and monitor the agent team

AGENTS_DIR="/home/m1ndb0t/Desktop/J1MSKY/agents"
AGENTS=("scout" "vitals" "archivist")

color_green='\033[0;32m'
color_red='\033[0;31m'
color_yellow='\033[1;33m'
color_cyan='\033[0;36m'
color_reset='\033[0m'

start_agents() {
    echo -e "${color_cyan}◈ Starting J1MSKY Agent Team ◈${color_reset}"
    for agent in "${AGENTS[@]}"; do
        if pgrep -f "${agent}.py" > /dev/null; then
            echo -e "  ${color_yellow}⚡ $agent already running${color_reset}"
        else
            python3 "$AGENTS_DIR/${agent}.py" > /tmp/${agent}.log 2>&1 &
            echo -e "  ${color_green}✓ $agent started (PID: $!)${color_reset}"
        fi
    done
    echo ""
}

stop_agents() {
    echo -e "${color_cyan}◈ Stopping J1MSKY Agent Team ◈${color_reset}"
    for agent in "${AGENTS[@]}"; do
        pids=$(pgrep -f "${agent}.py" | grep -v grep)
        if [ -n "$pids" ]; then
            echo "$pids" | xargs kill 2>/dev/null
            echo -e "  ${color_red}✗ $agent stopped${color_reset}"
        else
            echo -e "  ${color_yellow}○ $agent not running${color_reset}"
        fi
    done
    echo ""
}

status_agents() {
    echo -e "${color_cyan}◈ Agent Team Status ◈${color_reset}"
    echo ""
    
    for agent in "${AGENTS[@]}"; do
        pid=$(pgrep -f "${agent}.py" | grep -v grep | head -1)
        status_file="/tmp/agents/${agent}_status.json"
        
        if [ -n "$pid" ]; then
            if [ -f "$status_file" ]; then
                status=$(cat "$status_file" | grep -o '"status": "[^"]*"' | cut -d'"' -f4)
                echo -e "  ${color_green}● $agent${color_reset} | PID: $pid | Status: $status"
            else
                echo -e "  ${color_green}● $agent${color_reset} | PID: $pid | Status: unknown"
            fi
        else
            echo -e "  ${color_red}○ $agent${color_reset} | Not running"
        fi
    done
    
    echo ""
    echo -e "${color_cyan}◈ Recent Activity ◈${color_reset}"
    for agent in "${AGENTS[@]}"; do
        log_file="/tmp/${agent}.log"
        if [ -f "$log_file" ]; then
            last_line=$(tail -1 "$log_file" 2>/dev/null)
            echo -e "  ${color_cyan}$agent:${color_reset} $last_line"
        fi
    done
    echo ""
}

logs_agents() {
    agent=$2
    if [ -z "$agent" ]; then
        echo "Usage: $0 logs [scout|vitals|archivist]"
        exit 1
    fi
    
    log_file="/tmp/${agent}.log"
    if [ -f "$log_file" ]; then
        tail -20 "$log_file"
    else
        echo "No log file for $agent"
    fi
}

case "$1" in
    start)
        start_agents
        ;;
    stop)
        stop_agents
        ;;
    restart)
        stop_agents
        sleep 2
        start_agents
        ;;
    status)
        status_agents
        ;;
    logs)
        logs_agents "$@"
        ;;
    *)
        echo "J1MSKY Agent Coordinator"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs <agent>}"
        echo ""
        echo "Commands:"
        echo "  start          - Start all agents"
        echo "  stop           - Stop all agents"
        echo "  restart        - Restart all agents"
        echo "  status         - Show agent status"
        echo "  logs <agent>   - Show logs for agent"
        echo ""
        echo "Agents: scout, vitals, archivist"
        exit 1
        ;;
esac
