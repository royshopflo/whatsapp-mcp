#!/bin/bash

# WhatsApp Bridge Monitor Script
# This script monitors the bridge and restarts it if it goes down
# Can be run as a cron job for automatic monitoring

SCRIPT_DIR="/Users/macbook/whatsapp-mcp-2"
BRIDGE_SCRIPT="$SCRIPT_DIR/start_whatsapp_bridge.sh"
LOG_DIR="$SCRIPT_DIR/logs"
MONITOR_LOG="$LOG_DIR/bridge_monitor.log"

# Create logs directory
mkdir -p "$LOG_DIR"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S IST')] $1" | tee -a "$MONITOR_LOG"
}

# Function to check if bridge is healthy
is_bridge_healthy() {
    # Check if the bridge process is running
    if ! "$BRIDGE_SCRIPT" status > /dev/null 2>&1; then
        return 1
    fi
    
    # Check if API is responding
    if ! curl -s --connect-timeout 10 http://localhost:8080/api > /dev/null 2>&1; then
        return 1
    fi
    
    return 0
}

# Function to restart bridge
restart_bridge() {
    log_message "🔄 Bridge is down, attempting restart..."
    
    if "$BRIDGE_SCRIPT" restart; then
        log_message "✅ Bridge restarted successfully"
        
        # Wait and verify
        sleep 15
        if is_bridge_healthy; then
            log_message "✅ Bridge is healthy after restart"
            return 0
        else
            log_message "❌ Bridge still unhealthy after restart"
            return 1
        fi
    else
        log_message "❌ Failed to restart bridge"
        return 1
    fi
}

# Main monitoring logic
log_message "🔍 Checking WhatsApp bridge health..."

if is_bridge_healthy; then
    log_message "✅ Bridge is healthy"
    exit 0
else
    log_message "❌ Bridge is not healthy"
    
    # Attempt restart
    if restart_bridge; then
        log_message "✅ Bridge monitoring completed successfully"
        exit 0
    else
        log_message "❌ Bridge monitoring failed - manual intervention required"
        exit 1
    fi
fi 