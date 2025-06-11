#!/bin/bash

# Setup CRON job for WhatsApp Analysis
# Schedules analysis to run at 10AM, 2PM, and 6PM IST

SCRIPT_DIR="/Users/macbook/whatsapp-mcp-2"
CRON_SCRIPT="$SCRIPT_DIR/automated_analysis.sh"
CRON_JOB_COMMENT="# WhatsApp Analysis - Auto-send to Shopflo onboarding-internal"

echo "🔧 Setting up CRON job for WhatsApp Analysis"
echo "============================================"

# Check if script exists
if [ ! -f "$CRON_SCRIPT" ]; then
    echo "❌ Error: Script not found: $CRON_SCRIPT"
    exit 1
fi

# Make sure script is executable
chmod +x "$CRON_SCRIPT"

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

echo "✅ Script found and executable: $CRON_SCRIPT"

# Backup current crontab
echo "📋 Backing up current crontab..."
crontab -l > "$SCRIPT_DIR/crontab_backup_$(date +%Y%m%d_%H%M%S).txt" 2>/dev/null || echo "No existing crontab found"

# Create new cron entries
CRON_ENTRIES="
$CRON_JOB_COMMENT
0 10 * * * $CRON_SCRIPT >/dev/null 2>&1
0 14 * * * $CRON_SCRIPT >/dev/null 2>&1
0 18 * * * $CRON_SCRIPT >/dev/null 2>&1
"

echo "📅 Adding CRON jobs for:"
echo "   - 10:00 AM IST (Daily)"
echo "   - 02:00 PM IST (Daily)" 
echo "   - 06:00 PM IST (Daily)"

# Get current crontab (if any) and add new entries
(crontab -l 2>/dev/null | grep -v "$CRON_JOB_COMMENT" | grep -v "$CRON_SCRIPT"; echo "$CRON_ENTRIES") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ CRON job setup successful!"
    echo ""
    echo "📋 Current crontab:"
    echo "==================="
    crontab -l
    echo ""
    echo "📝 Log files will be stored in: $SCRIPT_DIR/logs/"
    echo "🔍 Monitor logs with: tail -f $SCRIPT_DIR/logs/analysis_$(date +%Y%m%d).log"
    echo ""
    echo "⚙️  To remove the cron job later, run:"
    echo "   crontab -e"
    echo "   (Then delete the WhatsApp Analysis lines)"
    echo ""
    echo "🚀 The analysis will now run automatically at:"
    echo "   - 10:00 AM IST"
    echo "   - 02:00 PM IST"
    echo "   - 06:00 PM IST"
    echo ""
    echo "📱 Messages will be sent to 'Shopflo onboarding-internal' group"
else
    echo "❌ Failed to setup CRON job"
    exit 1
fi 