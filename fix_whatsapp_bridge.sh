#!/bin/bash

# WhatsApp Bridge Fix Script
# This script helps fix connection issues with the WhatsApp bridge

set -e

BRIDGE_DIR="whatsapp-bridge"
PID_FILE="whatsapp_bridge.pid"
LOG_FILE="logs/whatsapp_bridge.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Function to clean up processes
cleanup() {
    log "Cleaning up existing processes..."
    pkill -f "./main" 2>/dev/null || true
    pkill -f "whatsapp-bridge" 2>/dev/null || true
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
    rm -f "$PID_FILE"
    sleep 3
}

# Function to check if bridge is connected
check_connection() {
    if curl -s http://localhost:8081/ >/dev/null 2>&1; then
        # Test sending a message
        response=$(curl -s -X POST http://localhost:8081/api/send \
            -H "Content-Type: application/json" \
            -d '{"recipient":"test@test.com","message":"test"}' 2>/dev/null || echo '{"success":false,"message":"API not responding"}')
        
        if echo "$response" | grep -q '"success":true'; then
            return 0
        elif echo "$response" | grep -q "Not connected to WhatsApp"; then
            return 1
        else
            return 2
        fi
    else
        return 3
    fi
}

# Function to start bridge with phone pairing
start_with_phone() {
    log "Starting bridge with phone pairing..."
    
    # Get phone number from user
    echo -n "Enter your WhatsApp phone number (with country code, e.g., +1234567890): "
    read phone_number
    
    if [ -z "$phone_number" ]; then
        error "Phone number is required"
        exit 1
    fi
    
    cd "$BRIDGE_DIR"
    
    # Start bridge with phone pairing
    log "Starting bridge with phone number: $phone_number"
    ./main --phone "$phone_number" &
    local bridge_pid=$!
    
    # Save PID
    echo "$bridge_pid" > "../$PID_FILE"
    
    # Wait for startup
    sleep 5
    
    # Check if process is still running
    if kill -0 "$bridge_pid" 2>/dev/null; then
        success "Bridge started with PID $bridge_pid"
        log "Waiting for phone pairing to complete..."
        
        # Wait up to 3 minutes for authentication
        for i in {1..180}; do
            if check_connection; then
                success "Bridge is connected to WhatsApp!"
                return 0
            fi
            
            if [ $((i % 30)) -eq 0 ]; then
                log "Still waiting for authentication... (${i}s)"
            fi
            
            sleep 1
        done
        
        error "Phone pairing timed out"
        return 1
    else
        error "Bridge failed to start"
        return 1
    fi
}

# Function to start bridge with QR code
start_with_qr() {
    log "Starting bridge with QR code authentication..."
    
    cd "$BRIDGE_DIR"
    
    # Start bridge
    ./main &
    local bridge_pid=$!
    
    # Save PID
    echo "$bridge_pid" > "../$PID_FILE"
    
    # Wait for startup
    sleep 5
    
    # Check if process is still running
    if kill -0 "$bridge_pid" 2>/dev/null; then
        success "Bridge started with PID $bridge_pid"
        log "QR code should be displayed in the terminal"
        log "Please scan the QR code with your WhatsApp app"
        
        # Wait up to 3 minutes for authentication
        for i in {1..180}; do
            if check_connection; then
                success "Bridge is connected to WhatsApp!"
                return 0
            fi
            
            if [ $((i % 30)) -eq 0 ]; then
                log "Still waiting for QR code scan... (${i}s)"
            fi
            
            sleep 1
        done
        
        error "QR code authentication timed out"
        return 1
    else
        error "Bridge failed to start"
        return 1
    fi
}

# Main execution
main() {
    log "WhatsApp Bridge Fix Script"
    log "=========================="
    
    # Clean up existing processes
    cleanup
    
    # Check current status
    log "Checking current bridge status..."
    if check_connection; then
        success "Bridge is already connected to WhatsApp!"
        return 0
    fi
    
    # Ask user for authentication method
    echo ""
    echo "Choose authentication method:"
    echo "1. QR Code (recommended)"
    echo "2. Phone Pairing"
    echo "3. Exit"
    echo ""
    echo -n "Enter your choice (1-3): "
    read choice
    
    case $choice in
        1)
            start_with_qr
            ;;
        2)
            start_with_phone
            ;;
        3)
            log "Exiting..."
            exit 0
            ;;
        *)
            error "Invalid choice"
            exit 1
            ;;
    esac
    
    # Final check
    if check_connection; then
        success "WhatsApp bridge is now connected and ready!"
        log "You can now run your cron jobs"
    else
        error "Failed to connect bridge to WhatsApp"
        log "Please try again or check the logs"
    fi
}

# Run main function
main "$@" 