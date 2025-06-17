#!/bin/bash

# Comprehensive System Status Checker
# This script checks all components of the WhatsApp automation system

echo "🔍 WhatsApp Automation System Status Check"
echo "=========================================="
echo

# Check 1: Cron daemon
echo "1️⃣ Cron Daemon Status:"
if ps aux | grep -v grep | grep cron > /dev/null; then
    echo "   ✅ Cron daemon is running"
else
    echo "   ❌ Cron daemon is NOT running"
fi
echo

# Check 2: Cron jobs
echo "2️⃣ Scheduled Cron Jobs:"
if crontab -l 2>/dev/null | grep -q "automated_analysis.sh"; then
    echo "   ✅ WhatsApp analysis cron jobs are configured"
    crontab -l | grep "automated_analysis.sh" | head -3
else
    echo "   ❌ WhatsApp analysis cron jobs are NOT configured"
fi

if crontab -l 2>/dev/null | grep -q "bridge_monitor.sh"; then
    echo "   ✅ Bridge monitoring cron job is configured"
    crontab -l | grep "bridge_monitor.sh"
else
    echo "   ❌ Bridge monitoring cron job is NOT configured"
fi
echo

# Check 3: WhatsApp Bridge Process
echo "3️⃣ WhatsApp Bridge Process:"
if ps aux | grep -v grep | grep "go run main.go" > /dev/null; then
    echo "   ✅ WhatsApp bridge process is running"
    ps aux | grep -v grep | grep "go run main.go" | while read line; do
        echo "      $line"
    done
else
    echo "   ❌ WhatsApp bridge process is NOT running"
fi
echo

# Check 4: Port 8080 availability
echo "4️⃣ Port 8080 Status:"
if curl -s --connect-timeout 5 http://localhost:8080/api > /dev/null 2>&1; then
    echo "   ✅ Port 8080 is responding"
else
    echo "   ❌ Port 8080 is NOT responding"
fi

# Check what's using port 8080
PORT_USER=$(lsof -ti:8080 2>/dev/null)
if [ -n "$PORT_USER" ]; then
    echo "   🔍 Processes using port 8080:"
    lsof -i:8080 2>/dev/null | head -10
else
    echo "   ℹ️  No processes found using port 8080"
fi
echo

# Check 5: WhatsApp API Connection Test
echo "5️⃣ WhatsApp API Connection:"
API_RESPONSE=$(curl -s -X POST http://localhost:8080/api/send \
    -H "Content-Type: application/json" \
    -d '{"recipient":"test","message":"test"}' 2>/dev/null)

if echo "$API_RESPONSE" | grep -q '"success"'; then
    if echo "$API_RESPONSE" | grep -q '"success":true'; then
        echo "   ✅ WhatsApp API is connected and working"
    else
        echo "   ⚠️  WhatsApp API responding but not connected to WhatsApp"
        echo "      Response: $API_RESPONSE"
    fi
else
    echo "   ❌ WhatsApp API is NOT responding"
fi
echo

# Check 6: macOS Launch Agent
echo "6️⃣ macOS Launch Agent:"
PLIST_FILE="$HOME/Library/LaunchAgents/com.shopflo.whatsapp-bridge.plist"
if [ -f "$PLIST_FILE" ]; then
    echo "   ✅ Launch agent plist file exists"
    if launchctl list | grep -q "whatsapp-bridge"; then
        echo "   ✅ Launch agent is loaded"
    else
        echo "   ⚠️  Launch agent plist exists but not loaded"
    fi
else
    echo "   ❌ Launch agent plist file does NOT exist"
fi
echo

# Check 7: Log Files
echo "7️⃣ Recent Log Activity:"
LOG_DIR="/Users/macbook/whatsapp-mcp-2/logs"
if [ -d "$LOG_DIR" ]; then
    echo "   📁 Log directory exists"
    
    # Check today's analysis log
    TODAY_LOG="$LOG_DIR/analysis_$(date +%Y%m%d).log"
    if [ -f "$TODAY_LOG" ]; then
        echo "   📄 Today's analysis log exists"
        LAST_RUN=$(tail -1 "$TODAY_LOG" | grep -o '\[.*\]' | head -1)
        echo "      Last activity: $LAST_RUN"
    else
        echo "   ⚠️  No analysis log for today"
    fi
    
    # Check bridge log
    BRIDGE_LOG="$LOG_DIR/whatsapp_bridge.log"
    if [ -f "$BRIDGE_LOG" ]; then
        echo "   📄 Bridge log exists"
        if tail -5 "$BRIDGE_LOG" | grep -q "Connected to WhatsApp"; then
            echo "      ✅ Recent WhatsApp connection found in logs"
        else
            echo "      ⚠️  No recent WhatsApp connection in logs"
        fi
    else
        echo "   ⚠️  No bridge log found"
    fi
else
    echo "   ❌ Log directory does NOT exist"
fi
echo

# Check 8: System Health Summary
echo "8️⃣ System Health Summary:"
echo "=========================================="

# Count issues
ISSUES=0

# Check each component
if ! ps aux | grep -v grep | grep cron > /dev/null; then
    echo "❌ Cron daemon not running"
    ((ISSUES++))
fi

if ! crontab -l 2>/dev/null | grep -q "automated_analysis.sh"; then
    echo "❌ Analysis cron jobs missing"
    ((ISSUES++))
fi

if ! ps aux | grep -v grep | grep "go run main.go" > /dev/null; then
    echo "❌ WhatsApp bridge not running"
    ((ISSUES++))
fi

if ! curl -s --connect-timeout 5 http://localhost:8080/api > /dev/null 2>&1; then
    echo "❌ Port 8080 not responding"
    ((ISSUES++))
fi

API_RESPONSE=$(curl -s -X POST http://localhost:8080/api/send \
    -H "Content-Type: application/json" \
    -d '{"recipient":"test","message":"test"}' 2>/dev/null)
if ! echo "$API_RESPONSE" | grep -q '"success":true'; then
    echo "❌ WhatsApp not connected"
    ((ISSUES++))
fi

if [ $ISSUES -eq 0 ]; then
    echo "🎉 ALL SYSTEMS ARE HEALTHY!"
    echo "   Your WhatsApp automation is working perfectly."
else
    echo "⚠️  Found $ISSUES issue(s) that need attention."
    echo "   Some components may need troubleshooting."
fi

echo
echo "🔧 Quick Commands:"
echo "  • Check bridge status:    ./start_whatsapp_bridge.sh status"
echo "  • Restart bridge:         ./start_whatsapp_bridge.sh restart"
echo "  • Test analysis:          ./automated_analysis.sh"
echo "  • Monitor logs:           ./monitor_logs.sh"
echo "  • Check this status:      ./check_system_status.sh" 