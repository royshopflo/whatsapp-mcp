#!/bin/bash

# Update Cron Jobs to use Detailed Analysis
# Replaces the summary analysis with individual group analysis

SCRIPT_DIR="/Users/macbook/whatsapp-mcp-3"
OLD_SCRIPT="$SCRIPT_DIR/send_analysis_to_priority_group.py"
NEW_SCRIPT="$SCRIPT_DIR/send_analysis_to_priority_group_detailed.py"
LOG_DIR="$SCRIPT_DIR/logs"

echo "🔄 Updating Cron Jobs to Detailed Analysis"
echo "=" * 60
echo "From: send_analysis_to_priority_group.py (summary)"
echo "To:   send_analysis_to_priority_group_detailed.py (individual groups)"
echo "=" * 60

# Backup current crontab
echo "📋 Backing up current crontab..."
BACKUP_FILE="$SCRIPT_DIR/crontab_backup_detailed_$(date +%Y%m%d_%H%M%S).txt"
crontab -l > "$BACKUP_FILE" 2>/dev/null || echo "# No existing crontab" > "$BACKUP_FILE"
echo "✅ Crontab backed up to: $BACKUP_FILE"

# Create temporary cron file
TEMP_CRON=$(mktemp)

# Add existing cron jobs (excluding priority analysis jobs)
crontab -l 2>/dev/null | grep -v "send_analysis_to_priority_group" > "$TEMP_CRON" || true

# Add updated priority analysis cron jobs with detailed script
echo "" >> "$TEMP_CRON"
echo "# Priority Analysis WhatsApp Notifications - DETAILED Individual Group Analysis" >> "$TEMP_CRON"
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
echo "📝 Installing updated crontab with detailed analysis..."
crontab "$TEMP_CRON"

# Cleanup
rm "$TEMP_CRON"

echo "✅ Cron jobs successfully updated!"
echo ""
echo "📋 Updated Schedule (Now with Individual Group Analysis):"
echo "• 10:00 AM - Detailed individual group analysis"
echo "• 11:00 AM - Detailed individual group analysis"
echo "• 12:00 PM - Detailed individual group analysis"
echo "• 01:00 PM - Detailed individual group analysis"
echo "• 02:00 PM - Detailed individual group analysis"
echo "• 03:00 PM - Detailed individual group analysis"
echo "• 04:00 PM - Detailed individual group analysis"
echo "• 05:00 PM - Detailed individual group analysis"
echo "• 06:00 PM - Detailed individual group analysis"
echo "• 07:00 PM - Detailed individual group analysis"
echo ""
echo "🔍 What's New in Detailed Analysis:"
echo "• ✅ Individual status for each group (CRITICAL/AT_RISK/STABLE/etc.)"
echo "• ✅ Specific sentiment analysis per group"
echo "• ✅ Individual issues identified for each group"
echo "• ✅ Prioritized action items by group severity"
echo "• ✅ 18+ groups analyzed individually"
echo ""
echo "📁 Logs will be saved to: $LOG_DIR/priority_analysis_YYYYMMDD.log"

# Verify cron installation
echo ""
echo "🔍 Verifying cron installation..."
CRON_COUNT=$(crontab -l | grep -c "send_analysis_to_priority_group_detailed.py" || true)
echo "✅ Found $CRON_COUNT detailed priority analysis cron jobs installed"

if [ "$CRON_COUNT" -eq 10 ]; then
    echo ""
    echo "🎉 SUCCESS! All 10 detailed analysis cron jobs have been installed."
    echo "📱 Priority inbox check group will now receive INDIVIDUAL group analysis every hour."
    echo ""
    echo "📊 Sample of what each report includes:"
    echo "• 🚨 Solutions War Room - CRITICAL (38.5% negative sentiment)"
    echo "• ⚠️ [Group Name] - AT RISK (15% negative sentiment)"
    echo "• ✅ [Group Name] - STABLE (2% negative sentiment)"
    echo "• 😴 [Group Name] - QUIET (no customer activity)"
    echo "• 💤 [Group Name] - INACTIVE (no messages)"
    echo ""
    echo "🔄 To test the new detailed analysis:"
    echo "   python3 $NEW_SCRIPT"
else
    echo ""
    echo "⚠️ WARNING: Expected 10 cron jobs but found $CRON_COUNT"
    echo "Please check the cron installation manually with: crontab -l"
fi 