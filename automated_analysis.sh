#!/bin/bash

# Automated WhatsApp Analysis Script
# Runs analysis and sends to Shopflo onboarding-internal group
# Designed for CRON execution at 10AM, 2PM, and 6PM IST

# Configuration
SCRIPT_DIR="/Users/macbook/whatsapp-mcp-2"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/analysis_$(date +%Y%m%d).log"
PYTHON_SCRIPT="$SCRIPT_DIR/send_to_whatsapp_group.py"
LOCK_FILE="/tmp/whatsapp_analysis.lock"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S IST')] $1" | tee -a "$LOG_FILE"
}

# Function to cleanup on exit
cleanup() {
    rm -f "$LOCK_FILE"
    log_message "Script execution completed"
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Check if script is already running
if [ -f "$LOCK_FILE" ]; then
    log_message "ERROR: Another instance is already running (lock file exists: $LOCK_FILE)"
    exit 1
fi

# Create lock file
echo $$ > "$LOCK_FILE"

log_message "=============================================="
log_message "STARTING AUTOMATED WHATSAPP ANALYSIS"
log_message "=============================================="

# Change to script directory
cd "$SCRIPT_DIR" || {
    log_message "ERROR: Failed to change to script directory: $SCRIPT_DIR"
    exit 1
}

log_message "Working directory: $(pwd)"

# Check if WhatsApp bridge is running
log_message "Checking WhatsApp bridge status..."
if ! curl -s http://localhost:8080/api >/dev/null 2>&1; then
    log_message "ERROR: WhatsApp bridge is not running on localhost:8080"
    log_message "Please start the WhatsApp bridge before running this script"
    exit 1
fi

log_message "✅ WhatsApp bridge is running"

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    log_message "ERROR: Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

log_message "✅ Python script found: $PYTHON_SCRIPT"

# Run the analysis and send message
log_message "Running WhatsApp analysis and message sender..."

# Use uv to run the script with proper dependencies
if command -v uv >/dev/null 2>&1; then
    log_message "Using uv package manager..."
    uv run --project whatsapp-mcp-server python send_to_whatsapp_group.py >> "$LOG_FILE" 2>&1
    RESULT=$?
else
    log_message "Using system python..."
    python3 "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1
    RESULT=$?
fi

# Check result
if [ $RESULT -eq 0 ]; then
    log_message "✅ SUCCESS: Analysis sent successfully to WhatsApp group"
    log_message "📱 Message delivered to 'Shopflo onboarding-internal' group"
else
    log_message "❌ FAILED: Script execution failed with exit code: $RESULT"
    log_message "Check the log for detailed error information"
fi

log_message "=============================================="
log_message "AUTOMATED ANALYSIS COMPLETED"
log_message "=============================================="

exit $RESULT 