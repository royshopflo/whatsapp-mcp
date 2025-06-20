#!/bin/bash

# Enhanced CRON Setup for WhatsApp Analysis
# Schedules analysis to run at 10AM, 11AM, 12PM, 2PM, 4PM, and 6PM IST
# Updated schedule for more frequent monitoring

SCRIPT_DIR="/Users/macbook/whatsapp-mcp-2"
CRON_SCRIPT="$SCRIPT_DIR/automated_analysis.sh"
CRON_JOB_COMMENT="# WhatsApp Analysis - Enhanced Schedule - Auto-send to Shopflo onboarding-internal"

echo "🔧 Setting up Enhanced CRON job for WhatsApp Analysis"
echo "===================================================="
echo "📅 New Schedule: 10AM, 11AM, 12PM, 2PM, 4PM, 6PM IST"
echo "===================================================="

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

# Remove any existing WhatsApp Analysis cron jobs
echo "🧹 Removing any existing WhatsApp Analysis cron jobs..."
(crontab -l 2>/dev/null | grep -v "WhatsApp Analysis" | grep -v "$CRON_SCRIPT") | crontab - 2>/dev/null || true

# Create new cron entries - IST times (system should be configured for IST)
# Note: These times assume the system is running in IST timezone
CRON_ENTRIES="
$CRON_JOB_COMMENT
0 10 * * * $CRON_SCRIPT >/dev/null 2>&1
0 11 * * * $CRON_SCRIPT >/dev/null 2>&1
0 12 * * * $CRON_SCRIPT >/dev/null 2>&1
0 14 * * * $CRON_SCRIPT >/dev/null 2>&1
0 16 * * * $CRON_SCRIPT >/dev/null 2>&1
0 18 * * * $CRON_SCRIPT >/dev/null 2>&1
"

echo "📅 Adding CRON jobs for IST times:"
echo "   - 10:00 AM IST (Daily)"
echo "   - 11:00 AM IST (Daily)"
echo "   - 12:00 PM IST (Daily)"
echo "   - 02:00 PM IST (Daily)" 
echo "   - 04:00 PM IST (Daily)"
echo "   - 06:00 PM IST (Daily)"

# Get current crontab (if any) and add new entries
(crontab -l 2>/dev/null; echo "$CRON_ENTRIES") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Enhanced CRON job setup successful!"
    echo ""
    echo "📋 Current crontab:"
    echo "==================="
    crontab -l
    echo ""
    echo "🕐 System timezone info:"
    echo "========================"
    echo "Current system time: $(date)"
    echo "System timezone: $(date +%Z)"
    echo ""
    echo "📝 Log files will be stored in: $SCRIPT_DIR/logs/"
    echo "🔍 Monitor logs with: tail -f $SCRIPT_DIR/logs/analysis_$(date +%Y%m%d).log"
    echo ""
    echo "⚙️  To modify the cron job later, run:"
    echo "   crontab -e"
    echo ""
    echo "🚀 The analysis will now run automatically 6 times daily at:"
    echo "   ☀️  10:00 AM IST (Morning analysis)"
    echo "   🌅 11:00 AM IST (Late morning check)"
    echo "   🌞 12:00 PM IST (Noon analysis)"
    echo "   🌤️  02:00 PM IST (Afternoon analysis)"
    echo "   🌆 04:00 PM IST (Late afternoon check)"
    echo "   🌇 06:00 PM IST (Evening analysis)"
    echo ""
    echo "📱 Messages will be sent to 'Shopflo onboarding-internal' group"
    echo "💡 Dynamic analysis periods will adjust based on execution time"
else
    echo "❌ Failed to setup enhanced CRON job"
    exit 1
fi

echo ""
echo "🎯 Next scheduled runs:"
echo "======================"
echo "Today's remaining runs:"
current_hour=$(date +%H)
if [ $current_hour -lt 10 ]; then
    echo "   - 10:00 AM IST"
fi
if [ $current_hour -lt 11 ]; then
    echo "   - 11:00 AM IST"
fi
if [ $current_hour -lt 12 ]; then
    echo "   - 12:00 PM IST"
fi
if [ $current_hour -lt 14 ]; then
    echo "   - 02:00 PM IST"
fi
if [ $current_hour -lt 16 ]; then
    echo "   - 04:00 PM IST"
fi
if [ $current_hour -lt 18 ]; then
    echo "   - 06:00 PM IST"
fi

echo ""
echo "✨ Setup complete! Your WhatsApp analysis is now running on an enhanced schedule." 