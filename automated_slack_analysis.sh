#!/bin/bash

# 📊 Automated WhatsApp Analysis Sender to Slack
# Enhanced version with comprehensive logging and error handling
# Based on automated_analysis.sh but sends to Slack instead of WhatsApp

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
DATE=$(date '+%Y%m%d')
TIME=$(date '+%Y-%m-%d %H:%M:%S %Z')
LOG_FILE="$LOG_DIR/slack_analysis_$DATE.log"
PYTHON_SCRIPT="$SCRIPT_DIR/send_to_slack_group.py"
LOCK_FILE="$SCRIPT_DIR/slack_analysis.lock"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log_message() {
    local message="$1"
    echo "[$TIME] $message" | tee -a "$LOG_FILE"
}

# Error logging function
log_error() {
    local message="$1"
    echo -e "${RED}[$TIME] ERROR: $message${NC}" | tee -a "$LOG_FILE"
}

# Success logging function
log_success() {
    local message="$1"
    echo -e "${GREEN}[$TIME] SUCCESS: $message${NC}" | tee -a "$LOG_FILE"
}

# Warning logging function
log_warning() {
    local message="$1"
    echo -e "${YELLOW}[$TIME] WARNING: $message${NC}" | tee -a "$LOG_FILE"
}

# Info logging function
log_info() {
    local message="$1"
    echo -e "${BLUE}[$TIME] INFO: $message${NC}" | tee -a "$LOG_FILE"
}

# Cleanup function
cleanup() {
    if [ -f "$LOCK_FILE" ]; then
        rm -f "$LOCK_FILE"
        log_info "Lock file removed"
    fi
}

# Set trap for cleanup
trap cleanup EXIT

# Create logs directory if it doesn't exist
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
    log_info "Created logs directory: $LOG_DIR"
fi

# Start logging
log_message "=========================================="
log_message "STARTING AUTOMATED SLACK ANALYSIS"
log_message "=========================================="

# Check for lock file (prevent concurrent executions)
if [ -f "$LOCK_FILE" ]; then
    log_error "Another instance is already running (lock file exists: $LOCK_FILE)"
    log_error "If this is incorrect, remove the lock file: rm $LOCK_FILE"
    exit 1
fi

# Create lock file
echo $$ > "$LOCK_FILE"
log_info "Created lock file with PID: $$"

# Environment checks
log_info "Environment checks starting..."

# Check if Slack webhook URL is configured
if [ -z "$SLACK_WEBHOOK_URL" ]; then
    log_error "SLACK_WEBHOOK_URL environment variable not set!"
    log_error "Please set it with: export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...'"
    log_error "Get your webhook URL from: https://api.slack.com/apps"
    exit 1
fi

log_success "✅ SLACK_WEBHOOK_URL is configured"

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    log_error "Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

log_success "✅ Python script found: $PYTHON_SCRIPT"

# Check if WhatsApp bridge is running (for data source)
BRIDGE_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health 2>/dev/null || echo "000")

if [ "$BRIDGE_HEALTH" = "200" ]; then
    log_success "✅ WhatsApp bridge is running and healthy"
elif [ "$BRIDGE_HEALTH" = "000" ]; then
    log_warning "⚠️ WhatsApp bridge connection failed - may affect analysis quality"
else
    log_warning "⚠️ WhatsApp bridge returned HTTP $BRIDGE_HEALTH - may affect analysis"
fi

# Check Python environment
PYTHON_CHECK=$(python3 -c "import requests, sys; print('OK')" 2>&1)
if echo "$PYTHON_CHECK" | grep -q "OK"; then
    log_success "✅ Python environment is ready"
    # Show warnings if they exist but don't treat them as errors
    if echo "$PYTHON_CHECK" | grep -v "OK" | grep -q "Warning"; then
        log_warning "Python SSL warnings detected (non-critical): $(echo "$PYTHON_CHECK" | grep Warning | head -1)"
    fi
else
    log_error "Python environment check failed: $PYTHON_CHECK"
    log_info "Attempting to install required packages..."
    pip install requests > /dev/null 2>&1
    
    # Re-check
    PYTHON_CHECK=$(python3 -c "import requests, sys; print('OK')" 2>&1)
    if echo "$PYTHON_CHECK" | grep -q "OK"; then
        log_success "✅ Python packages installed successfully"
    else
        log_error "Failed to install required Python packages"
        exit 1
    fi
fi

# Change to script directory
cd "$SCRIPT_DIR" || {
    log_error "Failed to change to script directory: $SCRIPT_DIR"
    exit 1
}

log_info "Changed to directory: $SCRIPT_DIR"

# Execute the Python script
log_info "Executing Slack analysis script..."
log_message "Command: python3 $PYTHON_SCRIPT"

# Capture both stdout and stderr
PYTHON_OUTPUT=$(python3 "$PYTHON_SCRIPT" 2>&1)
PYTHON_EXIT_CODE=$?

# Log the Python output
echo "$PYTHON_OUTPUT" | while IFS= read -r line; do
    log_info "Python: $line"
done

# Check execution result
if [ $PYTHON_EXIT_CODE -eq 0 ]; then
    log_success "✅ SUCCESS: Analysis sent successfully to Slack"
    log_success "📱 Message delivered to Slack channel"
    
    # Extract channel info from output if available
    CHANNEL_INFO=$(echo "$PYTHON_OUTPUT" | grep -o "Channel:.*" | head -1)
    if [ -n "$CHANNEL_INFO" ]; then
        log_info "📍 $CHANNEL_INFO"
    fi
    
    # Log success statistics
    MESSAGE_LENGTH=$(echo "$PYTHON_OUTPUT" | grep -o "Message length: [0-9]* characters" | head -1)
    if [ -n "$MESSAGE_LENGTH" ]; then
        log_info "📊 $MESSAGE_LENGTH"
    fi
    
else
    log_error "❌ FAILED: Python script exited with code $PYTHON_EXIT_CODE"
    log_error "📱 Message was NOT delivered to Slack"
    
    # Log specific error details
    ERROR_DETAILS=$(echo "$PYTHON_OUTPUT" | tail -5)
    log_error "Last 5 lines of output:"
    echo "$ERROR_DETAILS" | while IFS= read -r line; do
        log_error "  $line"
    done
fi

# Final status
log_message "=========================================="
if [ $PYTHON_EXIT_CODE -eq 0 ]; then
    log_success "AUTOMATED SLACK ANALYSIS COMPLETED SUCCESSFULLY"
    log_success "Next execution scheduled according to cron"
else
    log_error "AUTOMATED SLACK ANALYSIS FAILED"
    log_error "Check logs above for troubleshooting details"
fi
log_message "=========================================="

# Cleanup old log files (keep last 7 days)
find "$LOG_DIR" -name "slack_analysis_*.log" -mtime +7 -delete 2>/dev/null || true

exit $PYTHON_EXIT_CODE 