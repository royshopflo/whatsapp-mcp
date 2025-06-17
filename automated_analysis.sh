#!/bin/bash

# Automated WhatsApp Analysis Script with Retry Logic
# Runs analysis and sends to Shopflo onboarding-internal group
# Designed for CRON execution at 10AM, 2PM, and 6PM IST
# Now includes retry logic and automatic connection recovery

# Configuration
SCRIPT_DIR="/Users/macbook/whatsapp-mcp-2"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/analysis_$(date +%Y%m%d).log"
PYTHON_SCRIPT="$SCRIPT_DIR/send_to_whatsapp_group.py"
BRIDGE_MONITOR="$SCRIPT_DIR/bridge_monitor.sh"
LOCK_FILE="/tmp/whatsapp_analysis.lock"

# Retry configuration
MAX_RETRIES=3
RETRY_DELAY=60  # seconds between retries
CONNECTION_CHECK_DELAY=30  # seconds to wait after bridge restart

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
log_message "STARTING AUTOMATED WHATSAPP ANALYSIS (v2.0)"
log_message "=============================================="

# Change to script directory
cd "$SCRIPT_DIR" || {
    log_message "ERROR: Failed to change to script directory: $SCRIPT_DIR"
    exit 1
}

log_message "Working directory: $(pwd)"

# Function to check if WhatsApp bridge is running and connected
check_whatsapp_connection() {
    local attempt=1
    
    while [ $attempt -le 2 ]; do
        log_message "🔍 Checking WhatsApp bridge status (attempt $attempt/2)..."
        
        # Check if bridge API is responding
        if curl -s --connect-timeout 10 http://localhost:8080/api >/dev/null 2>&1; then
            # Check if WhatsApp is actually connected
            local status_response=$(curl -s --connect-timeout 10 http://localhost:8080/api/status 2>/dev/null || echo "")
            
            if [[ "$status_response" == *"connected"* ]] || [[ "$status_response" == *"true"* ]]; then
                log_message "✅ WhatsApp bridge is running and connected"
                return 0
            else
                log_message "⚠️  WhatsApp bridge is running but not connected to WhatsApp"
                
                if [ $attempt -eq 1 ]; then
                    log_message "🔄 Attempting to fix connection using bridge monitor..."
                    if [ -f "$BRIDGE_MONITOR" ]; then
                        "$BRIDGE_MONITOR" >> "$LOG_FILE" 2>&1
                        log_message "⏳ Waiting ${CONNECTION_CHECK_DELAY}s for connection to stabilize..."
                        sleep $CONNECTION_CHECK_DELAY
                    fi
                fi
            fi
        else
            log_message "❌ WhatsApp bridge API is not responding on localhost:8080"
            
            if [ $attempt -eq 1 ]; then
                log_message "🔄 Attempting to restart bridge using monitor script..."
                if [ -f "$BRIDGE_MONITOR" ]; then
                    "$BRIDGE_MONITOR" >> "$LOG_FILE" 2>&1
                    log_message "⏳ Waiting ${CONNECTION_CHECK_DELAY}s for bridge to start..."
                    sleep $CONNECTION_CHECK_DELAY
                fi
            fi
        fi
        
        attempt=$((attempt + 1))
    done
    
    log_message "❌ Failed to establish WhatsApp connection after 2 attempts"
    return 1
}

# Function to run the Python script with retry logic
run_analysis_with_retry() {
    local attempt=1
    local success=false
    
    while [ $attempt -le $MAX_RETRIES ] && [ "$success" = false ]; do
        log_message "🚀 Running WhatsApp analysis (attempt $attempt/$MAX_RETRIES)..."
        
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
            log_message "✅ SUCCESS: Analysis sent successfully to WhatsApp group (attempt $attempt)"
            log_message "📱 Message delivered to 'Shopflo onboarding-internal' group"
            success=true
            return 0
        else
            log_message "❌ FAILED: Script execution failed with exit code: $RESULT (attempt $attempt/$MAX_RETRIES)"
            
            if [ $attempt -lt $MAX_RETRIES ]; then
                log_message "⏳ Waiting ${RETRY_DELAY}s before retry..."
                log_message "🔄 Will check WhatsApp connection before next attempt..."
                sleep $RETRY_DELAY
                
                # Check and fix connection before retry
                if ! check_whatsapp_connection; then
                    log_message "⚠️  Connection check failed, but will still attempt retry"
                fi
            fi
        fi
        
        attempt=$((attempt + 1))
    done
    
    log_message "❌ FINAL FAILURE: All $MAX_RETRIES attempts failed"
    log_message "🔧 Manual intervention required - check WhatsApp Web connection"
    return 1
}

# Initial connection check
if ! check_whatsapp_connection; then
    log_message "❌ Initial WhatsApp connection check failed"
    log_message "⚠️  Proceeding with analysis anyway (retry logic will handle failures)"
fi

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    log_message "ERROR: Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

log_message "✅ Python script found: $PYTHON_SCRIPT"

# Run the analysis with retry logic
if run_analysis_with_retry; then
    log_message "🎉 AUTOMATED ANALYSIS COMPLETED SUCCESSFULLY"
    FINAL_RESULT=0
else
    log_message "💔 AUTOMATED ANALYSIS FAILED AFTER ALL RETRIES"
    log_message "📋 Troubleshooting steps:"
    log_message "   1. Check WhatsApp Web connection manually"
    log_message "   2. Restart WhatsApp bridge: ./start_whatsapp_bridge.sh restart"
    log_message "   3. Run manual test: ./send_to_whatsapp_group.py"
    log_message "   4. Check logs for detailed error information"
    FINAL_RESULT=1
fi

log_message "=============================================="
log_message "AUTOMATED ANALYSIS SESSION COMPLETED"
log_message "=============================================="

exit $FINAL_RESULT 