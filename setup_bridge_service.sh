#!/bin/bash

# WhatsApp Bridge Service Setup Script
# This script sets up the WhatsApp bridge to run automatically

SCRIPT_DIR="/Users/macbook/whatsapp-mcp-2"
BRIDGE_SCRIPT="$SCRIPT_DIR/start_whatsapp_bridge.sh"
MONITOR_SCRIPT="$SCRIPT_DIR/bridge_monitor.sh"

echo "🚀 Setting up WhatsApp Bridge Service"
echo "====================================="

# Make scripts executable
chmod +x "$BRIDGE_SCRIPT"
chmod +x "$MONITOR_SCRIPT"

echo "✅ Scripts made executable"

# Create launchd plist for macOS auto-startup
PLIST_FILE="$HOME/Library/LaunchAgents/com.shopflo.whatsapp-bridge.plist"

cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.shopflo.whatsapp-bridge</string>
    <key>ProgramArguments</key>
    <array>
        <string>$BRIDGE_SCRIPT</string>
        <string>start</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    <key>StandardOutPath</key>
    <string>$SCRIPT_DIR/logs/bridge_service.log</string>
    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/logs/bridge_service_error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/local/go/bin</string>
    </dict>
</dict>
</plist>
EOF

echo "✅ Created launchd service configuration"

# Load the service
launchctl unload "$PLIST_FILE" 2>/dev/null || true
launchctl load "$PLIST_FILE"

if [ $? -eq 0 ]; then
    echo "✅ WhatsApp bridge service loaded successfully"
else
    echo "❌ Failed to load service"
fi

# Update crontab to include bridge monitoring
echo "📋 Setting up bridge monitoring in cron..."

# Backup current crontab
crontab -l > "$SCRIPT_DIR/crontab_backup_bridge_$(date +%Y%m%d_%H%M%S).txt" 2>/dev/null || echo "No existing crontab found"

# Add bridge monitoring to cron (every 5 minutes)
MONITOR_CRON="# WhatsApp Bridge Monitor - Check every 5 minutes
*/5 * * * * $MONITOR_SCRIPT >/dev/null 2>&1"

# Get current crontab and add monitoring
(crontab -l 2>/dev/null | grep -v "WhatsApp Bridge Monitor" | grep -v "$MONITOR_SCRIPT"; echo "$MONITOR_CRON") | crontab -

echo "✅ Bridge monitoring added to cron"

# Start the bridge now
echo "🚀 Starting WhatsApp bridge..."
"$BRIDGE_SCRIPT" start

echo ""
echo "🎉 WhatsApp Bridge Service Setup Complete!"
echo "=========================================="
echo ""
echo "📋 What was configured:"
echo "  ✅ Bridge startup script: $BRIDGE_SCRIPT"
echo "  ✅ Bridge monitor script: $MONITOR_SCRIPT"
echo "  ✅ macOS service (auto-start on boot): Enabled"
echo "  ✅ Cron monitoring (every 5 minutes): Enabled"
echo "  ✅ Bridge started: Yes"
echo ""
echo "📁 Log files:"
echo "  • Bridge logs: $SCRIPT_DIR/logs/whatsapp_bridge.log"
echo "  • Monitor logs: $SCRIPT_DIR/logs/bridge_monitor.log"
echo "  • Service logs: $SCRIPT_DIR/logs/bridge_service.log"
echo ""
echo "🔧 Management commands:"
echo "  • Check status: $BRIDGE_SCRIPT status"
echo "  • Start bridge: $BRIDGE_SCRIPT start"
echo "  • Stop bridge: $BRIDGE_SCRIPT stop"
echo "  • Restart bridge: $BRIDGE_SCRIPT restart"
echo "  • Monitor health: $MONITOR_SCRIPT"
echo ""
echo "🔄 Service management:"
echo "  • Unload service: launchctl unload $PLIST_FILE"
echo "  • Load service: launchctl load $PLIST_FILE"
echo "  • Check service: launchctl list | grep whatsapp-bridge"
echo ""
echo "🚀 Your WhatsApp bridge will now:"
echo "  1. Start automatically when your Mac boots up"
echo "  2. Restart automatically if it crashes"
echo "  3. Be monitored every 5 minutes by cron"
echo "  4. Log all activity for troubleshooting"
echo ""
echo "✅ Your cron job for WhatsApp analysis should now work reliably!" 