#!/bin/bash

# Update Cron Jobs to use Fixed Analysis with Group Summaries
# Excludes internal groups from critical alerts and adds group descriptions

SCRIPT_DIR="/Users/macbook/whatsapp-mcp-3"
OLD_SCRIPT="$SCRIPT_DIR/send_analysis_to_priority_group_detailed.py"
NEW_SCRIPT="$SCRIPT_DIR/send_analysis_to_priority_group_fixed.py"
LOG_DIR="$SCRIPT_DIR/logs"

echo "🔄 Updating Cron Jobs to Fixed Analysis with Summaries"
echo "=" * 70
echo "From: send_analysis_to_priority_group_detailed.py"
echo "To:   send_analysis_to_priority_group_fixed.py"
echo ""
echo "✅ Fixes Applied:"
echo "• Solutions War Room marked as INTERNAL (not critical customer alert)"
echo "• Group summaries added for context"
echo "• Customer-focused critical alerts"
echo "• Enhanced categorization (Customer/Partner/Internal)"
echo "=" * 70

# Backup current crontab
echo "📋 Backing up current crontab..."
BACKUP_FILE="$SCRIPT_DIR/crontab_backup_fixed_$(date +%Y%m%d_%H%M%S).txt"
crontab -l > "$BACKUP_FILE" 2>/dev/null || echo "# No existing crontab" > "$BACKUP_FILE"
echo "✅ Crontab backed up to: $BACKUP_FILE"

# Create temporary cron file
TEMP_CRON=$(mktemp)

# Add existing cron jobs (excluding priority analysis jobs)
crontab -l 2>/dev/null | grep -v "send_analysis_to_priority_group" > "$TEMP_CRON" || true

# Add updated priority analysis cron jobs with fixed script
echo "" >> "$TEMP_CRON"
echo "# Priority Analysis WhatsApp Notifications - FIXED with Group Summaries & Customer Focus" >> "$TEMP_CRON"
echo "0 10 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 11 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 12 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 13 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 14 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 15 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 16 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 17 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 18 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 19 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"

# Install the updated crontab
echo "📝 Installing updated crontab with fixed analysis..."
crontab "$TEMP_CRON"

# Cleanup
rm "$TEMP_CRON"

echo "✅ Cron jobs successfully updated!"
echo ""
echo "📋 Enhanced Analysis Features:"
echo ""
echo "🏢 **Group Categories with Summaries:**"
echo "• CUSTOMER: E-commerce clients (Emma, BornGood, Boult, etc.)"
echo "• PARTNER: Integration partners (Indulgeo, Sirevest, etc.)"
echo "• INTERNAL: Team groups (Solutions War Room, CS, Sales)"
echo ""
echo "🚨 **Smart Alert System:**"
echo "• CUSTOMER issues = CRITICAL alerts (immediate action needed)"
echo "• PARTNER issues = monitored but not critical customer alerts"
echo "• INTERNAL issues = awareness only (no critical customer alerts)"
echo ""
echo "📊 **Sample Enhanced Report:**"
echo "\"📈 Categories: 🏢 Customers: 5 | 🤝 Partners: 8 | 🏠 Internal: 5\""
echo "\"🚨 CUSTOMER ALERTS: 1 groups need attention\""
echo "\"⚠️ 🏢 Shopflo <> Emma - E-commerce merchant client\""
echo "\"🏠 Solutions War Room - Internal technical issue resolution team\""
echo ""
echo "📁 Logs: $LOG_DIR/priority_analysis_YYYYMMDD.log"

# Verify cron installation
echo ""
echo "🔍 Verifying cron installation..."
CRON_COUNT=$(crontab -l | grep -c "send_analysis_to_priority_group_fixed.py" || true)
echo "✅ Found $CRON_COUNT fixed priority analysis cron jobs installed"

if [ "$CRON_COUNT" -eq 10 ]; then
    echo ""
    echo "🎉 SUCCESS! All 10 enhanced analysis cron jobs have been installed."
    echo "📱 Priority inbox check group will now receive:"
    echo "• ✅ Customer-focused critical alerts only"
    echo "• ✅ Group summaries for context"
    echo "• ✅ Proper categorization (Customer/Partner/Internal)"
    echo "• ✅ Solutions War Room correctly marked as internal"
    echo ""
    echo "🔄 To test the enhanced analysis:"
    echo "   python3 $NEW_SCRIPT"
else
    echo ""
    echo "⚠️ WARNING: Expected 10 cron jobs but found $CRON_COUNT"
    echo "Please check the cron installation manually with: crontab -l"
fi 