#!/bin/bash

# Safe WhatsApp Bridge Startup Script
# This script ensures proper database handling and prevents corruption

set -e  # Exit on any error

BRIDGE_DIR="whatsapp-bridge"
STORE_DIR="$BRIDGE_DIR/store"
WHATSAPP_DB="$STORE_DIR/whatsapp.db"
MESSAGES_DB="$STORE_DIR/messages.db"
LOG_FILE="logs/whatsapp_bridge.log"
PID_FILE="whatsapp_bridge.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1"
}

# Function to check if a process is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to stop the bridge gracefully
stop_bridge() {
    log "Stopping WhatsApp bridge..."
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        
        # Try graceful shutdown first
        if kill -TERM "$pid" 2>/dev/null; then
            log "Sent termination signal to process $pid"
            
            # Wait up to 10 seconds for graceful shutdown
            for i in {1..10}; do
                if ! kill -0 "$pid" 2>/dev/null; then
                    success "Process stopped gracefully"
                    rm -f "$PID_FILE"
                    return 0
                fi
                sleep 1
            done
            
            # Force kill if still running
            warning "Process did not stop gracefully, forcing shutdown..."
            kill -KILL "$pid" 2>/dev/null || true
        fi
        
        rm -f "$PID_FILE"
    fi
    
    # Kill any remaining bridge processes
    pkill -f "whatsapp-bridge" 2>/dev/null || true
    
    success "Bridge stopped"
}

# Function to check database integrity
check_database_integrity() {
    log "Checking database integrity..."
    
    if [ ! -d "$STORE_DIR" ]; then
        log "Creating store directory..."
        mkdir -p "$STORE_DIR"
    fi
    
    # Check WhatsApp database
    if [ -f "$WHATSAPP_DB" ]; then
        if ! sqlite3 "$WHATSAPP_DB" "PRAGMA integrity_check;" | grep -q "ok"; then
            error "WhatsApp database is corrupted!"
            return 1
        fi
        log "WhatsApp database integrity: OK"
    else
        log "WhatsApp database not found (will be created)"
    fi
    
    # Check Messages database
    if [ -f "$MESSAGES_DB" ]; then
        if ! sqlite3 "$MESSAGES_DB" "PRAGMA integrity_check;" | grep -q "ok"; then
            error "Messages database is corrupted!"
            return 1
        fi
        log "Messages database integrity: OK"
    else
        log "Messages database not found (will be created)"
    fi
    
    return 0
}

# Function to fix file permissions
fix_permissions() {
    log "Setting proper file permissions..."
    
    # Make sure the bridge binary is executable
    chmod +x "$BRIDGE_DIR/main" 2>/dev/null || true
    
    # Set proper permissions for store directory and databases
    chmod 755 "$STORE_DIR" 2>/dev/null || true
    chmod 644 "$WHATSAPP_DB" 2>/dev/null || true
    chmod 644 "$MESSAGES_DB" 2>/dev/null || true
    
    success "Permissions set"
}

# Function to start the bridge
start_bridge() {
    log "Starting WhatsApp bridge..."
    
    # Change to bridge directory
    cd "$BRIDGE_DIR"
    
    # Start the bridge in background and capture PID
    nohup ./main > "../$LOG_FILE" 2>&1 &
    local bridge_pid=$!
    
    # Save PID
    echo "$bridge_pid" > "../$PID_FILE"
    
    # Wait a moment for startup
    sleep 3
    
    # Check if process is still running
    if kill -0 "$bridge_pid" 2>/dev/null; then
        success "Bridge started with PID $bridge_pid"
        return 0
    else
        error "Bridge failed to start"
        rm -f "../$PID_FILE"
        return 1
    fi
}

# Function to monitor startup
monitor_startup() {
    log "Monitoring bridge startup..."
    
    # Wait up to 30 seconds for API to become available
    for i in {1..30}; do
        if curl -s -f "http://localhost:8080/" >/dev/null 2>&1; then
            success "Bridge API is responding"
            return 0
        fi
        
        if [ $((i % 5)) -eq 0 ]; then
            log "Waiting for API to start... (${i}s)"
        fi
        
        sleep 1
    done
    
    error "Bridge API did not start within timeout"
    return 1
}

# Main execution
main() {
    log "Safe WhatsApp Bridge Startup"
    log "=============================="
    
    # Check if already running
    if is_running; then
        warning "Bridge is already running"
        local pid=$(cat "$PID_FILE")
        log "Current PID: $pid"
        exit 0
    fi
    
    # Stop any existing processes
    stop_bridge
    
    # Wait a moment for cleanup
    sleep 2
    
    # Check database integrity
    if ! check_database_integrity; then
        error "Database integrity check failed"
        error "Run 'python3 fix_database_corruption.py' to repair databases"
        exit 1
    fi
    
    # Fix permissions
    fix_permissions
    
    # Create logs directory if needed
    mkdir -p logs
    
    # Start the bridge
    if ! start_bridge; then
        error "Failed to start bridge"
        exit 1
    fi
    
    # Monitor startup
    if ! monitor_startup; then
        error "Bridge startup monitoring failed"
        stop_bridge
        exit 1
    fi
    
    success "WhatsApp bridge is running successfully!"
    success "API available at: http://localhost:8080"
    success "Logs available at: $LOG_FILE"
    success "PID file: $PID_FILE"
    
    log "Use './safe_start_whatsapp_bridge.sh stop' to stop the bridge"
}

# Handle stop command
if [ "$1" = "stop" ]; then
    stop_bridge
    exit 0
fi

# Handle status command
if [ "$1" = "status" ]; then
    if is_running; then
        local pid=$(cat "$PID_FILE")
        success "Bridge is running with PID $pid"
        
        # Check API health
        if curl -s -f "http://localhost:8080/" >/dev/null 2>&1; then
            success "API is responding"
        else
            warning "API is not responding"
        fi
    else
        log "Bridge is not running"
    fi
    exit 0
fi

# Handle restart command
if [ "$1" = "restart" ]; then
    stop_bridge
    sleep 3
    main
    exit 0
fi

# Default action is to start
main 