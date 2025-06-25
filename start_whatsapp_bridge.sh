#!/bin/bash

# WhatsApp Bridge Startup Script
# This script starts the WhatsApp bridge and ensures it stays running

# Set PATH to include Go binary location
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"

SCRIPT_DIR="/Users/macbook/whatsapp-mcp-2"
BRIDGE_DIR="$SCRIPT_DIR/whatsapp-bridge"
LOG_DIR="$SCRIPT_DIR/logs"
BRIDGE_LOG="$LOG_DIR/whatsapp_bridge.log"
PID_FILE="/tmp/whatsapp_bridge.pid"

# Create logs directory
mkdir -p "$LOG_DIR"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S IST')] $1" | tee -a "$BRIDGE_LOG"
}

# Function to check if bridge is running
is_bridge_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    
    # Also check for any running bridge processes
    if ps aux | grep -v grep | grep -E "(./main|go run main.go)" | grep -q whatsapp-bridge; then
        return 0
    fi
    
    return 1
}

# Function to start the bridge
start_bridge() {
    log_message "Starting WhatsApp bridge..."
    
    cd "$BRIDGE_DIR" || {
        log_message "ERROR: Cannot change to bridge directory: $BRIDGE_DIR"
        exit 1
    }
    
    # Start the bridge in background using compiled binary (faster and more reliable)
    if [ -f "./main" ]; then
        log_message "Using compiled binary"
        nohup ./main >> "$BRIDGE_LOG" 2>&1 &
        BRIDGE_PID=$!
    else
        log_message "Using go run (compiling on-the-fly)"
        nohup go run main.go >> "$BRIDGE_LOG" 2>&1 &
        BRIDGE_PID=$!
    fi
    
    # Save PID
    echo $BRIDGE_PID > "$PID_FILE"
    
    log_message "WhatsApp bridge started with PID: $BRIDGE_PID"
    
    # Wait a moment and check if it's still running
    sleep 5
    if ps -p "$BRIDGE_PID" > /dev/null 2>&1; then
        log_message "✅ WhatsApp bridge is running successfully"
        
        # Test API endpoint
        sleep 10
        if curl -s http://localhost:8080/api > /dev/null 2>&1; then
            log_message "✅ WhatsApp bridge API is responding"
        else
            log_message "⚠️  Bridge started but API not responding yet (may need authentication)"
        fi
    else
        log_message "❌ WhatsApp bridge failed to start"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# Function to stop the bridge
stop_bridge() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        log_message "Stopping WhatsApp bridge (PID: $PID)..."
        kill "$PID" 2>/dev/null
        rm -f "$PID_FILE"
        log_message "WhatsApp bridge stopped"
    else
        log_message "WhatsApp bridge is not running"
    fi
}

# Function to restart the bridge
restart_bridge() {
    log_message "Restarting WhatsApp bridge..."
    stop_bridge
    sleep 2
    start_bridge
}

# Function to show status
show_status() {
    if is_bridge_running; then
        PID=$(cat "$PID_FILE")
        log_message "✅ WhatsApp bridge is running (PID: $PID)"
        
        # Test API
        if curl -s http://localhost:8080/api > /dev/null 2>&1; then
            log_message "✅ API is responding"
        else
            log_message "⚠️  API not responding"
        fi
    else
        log_message "❌ WhatsApp bridge is not running"
    fi
}

# Main script logic
case "${1:-start}" in
    start)
        if is_bridge_running; then
            log_message "WhatsApp bridge is already running"
            show_status
        else
            start_bridge
        fi
        ;;
    stop)
        stop_bridge
        ;;
    restart)
        restart_bridge
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo "  start   - Start the WhatsApp bridge (default)"
        echo "  stop    - Stop the WhatsApp bridge"
        echo "  restart - Restart the WhatsApp bridge"
        echo "  status  - Show bridge status"
        exit 1
        ;;
esac 