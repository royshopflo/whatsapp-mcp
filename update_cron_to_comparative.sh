#!/bin/bash

# Update Cron Jobs to use Comparative Analysis with Previous Period Comparison
# Shows trends and changes between current and previous 24-hour periods

SCRIPT_DIR="/Users/macbook/whatsapp-mcp-3"
OLD_SCRIPT="$SCRIPT_DIR/send_analysis_to_priority_group_fixed.py"
NEW_SCRIPT="$SCRIPT_DIR/send_analysis_to_priority_group_comparative.py"
LOG_DIR="$SCRIPT_DIR/logs"

echo "🔄 Updating Cron Jobs to Comparative Analysis with Trend Detection"
echo "======================================================================"
echo "From: send_analysis_to_priority_group_fixed.py"
echo "To:   send_analysis_to_priority_group_comparative.py"
echo ""
echo "📈 **NEW COMPARATIVE FEATURES:**"
echo "• Current Period vs Previous Period Analysis (24h each)"
echo "• Trend Detection: ⬇️✅ IMPROVING | ⬆️🔴 WORSENING | ➡️ STABLE"
echo "• Historical Context for Better Decision Making"
echo "• Customer Issues Prioritized by Trend Direction"
echo "• Period Comparison: Messages & Sentiment Changes"
echo ""
echo "🎯 **EXAMPLE COMPARATIVE INSIGHTS:**"
echo "• 'Emma group: increased from 5.2% to 16.7% negative (WORSENING)'"
echo "• 'BornGood: decreased from 12.1% to 3.2% negative (IMPROVING)'"
echo "• 'Previous Period: 07/21 13:44 - 07/22 13:44 IST'"
echo "• 'Current Period: 07/22 13:44 - 07/23 13:44 IST'"
echo "======================================================================"

# Backup current crontab
echo "📋 Backing up current crontab..."
BACKUP_FILE="$SCRIPT_DIR/crontab_backup_comparative_$(date +%Y%m%d_%H%M%S).txt"
crontab -l > "$BACKUP_FILE" 2>/dev/null || echo "# No existing crontab" > "$BACKUP_FILE"
echo "✅ Crontab backed up to: $BACKUP_FILE"

# Create temporary cron file
TEMP_CRON=$(mktemp)

# Add existing cron jobs (excluding priority analysis jobs)
crontab -l 2>/dev/null | grep -v "send_analysis_to_priority_group" > "$TEMP_CRON" || true

# Add comparative priority analysis cron jobs
echo "" >> "$TEMP_CRON"
echo "# Priority Analysis WhatsApp Notifications - COMPARATIVE with Previous Period Trends" >> "$TEMP_CRON"
echo "0 10 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_comparative_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 11 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_comparative_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 12 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_comparative_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 13 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_comparative_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 14 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_comparative_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 15 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_comparative_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 16 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_comparative_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 17 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_comparative_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 18 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_comparative_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 19 * * * cd $SCRIPT_DIR && /usr/bin/python3 $NEW_SCRIPT >> $LOG_DIR/priority_comparative_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"

# Install the updated crontab
echo "📝 Installing comparative analysis crontab..."
crontab "$TEMP_CRON"

# Cleanup
rm "$TEMP_CRON"

echo "✅ Comparative analysis cron jobs successfully updated!"
echo ""
echo "📊 **ENHANCED COMPARATIVE ANALYSIS FEATURES:**"
echo ""
echo "🔍 **TREND DETECTION:**"
echo "• ⬇️✅ IMPROVING: Groups with decreasing negative sentiment"
echo "• ⬆️🔴 WORSENING: Groups with increasing negative sentiment"  
echo "• 🔴 NEW ISSUES: Groups with new negative sentiment"
echo "• ➡️ STABLE: Groups with similar sentiment levels"
echo ""
echo "📈 **PERIOD COMPARISON:**"
echo "• Current Period: Last 24 hours"
echo "• Previous Period: 24 hours before that (48-24h ago)"
echo "• Message Count Changes: Shows activity trends"
echo "• Sentiment Ratio Changes: Shows mood trends"
echo ""
echo "🎯 **SMART PRIORITIZATION:**"
echo "• Customer groups with worsening trends = HIGHEST priority"
echo "• Critical issues get immediate action items"
echo "• At-risk groups monitored with trend context"
echo "• Improving groups acknowledged for positive progress"
echo ""
echo "📱 **SAMPLE COMPARATIVE REPORT:**"
echo "\"⬆️🔴 🚨 🏢 Shopflo <> Emma\""
echo "\"└ E-commerce merchant client - requires immediate attention\""
echo "\"└ Current: CRITICAL | Messages: 12 (16.7% negative)\""
echo "\"└ Previous: AT_RISK | Messages: 8 (5.2% negative)\""
echo "\"└ Latest Issue: 'payment gateway not working since morning'\""
echo ""
echo "\"⬇️✅ ✅ 🏢 BornGood || Shopflow\""
echo "\"└ Health & wellness brand customer\""
echo "\"└ Current: STABLE | Messages: 15 (3.2% negative)\""
echo "\"└ Previous: AT_RISK | Messages: 18 (12.1% negative)\""
echo ""
echo "📁 Logs: $LOG_DIR/priority_comparative_YYYYMMDD.log"

# Verify cron installation
echo ""
echo "🔍 Verifying comparative analysis cron installation..."
CRON_COUNT=$(crontab -l | grep -c "send_analysis_to_priority_group_comparative.py" || true)
echo "✅ Found $CRON_COUNT comparative analysis cron jobs installed"

if [ "$CRON_COUNT" -eq 10 ]; then
    echo ""
    echo "🎉 PERFECT! All 10 comparative analysis cron jobs installed successfully."
    echo ""
    echo "📱 Priority inbox check group will now receive ENHANCED analysis with:"
    echo "• ✅ Current vs Previous Period Comparison (48h total insight)"
    echo "• ✅ Trend Detection with Visual Indicators"
    echo "• ✅ Customer-Focused Alerts with Historical Context"
    echo "• ✅ Smart Prioritization Based on Trend Direction"
    echo "• ✅ Internal Groups Properly Categorized (No False Alerts)"
    echo "• ✅ Business Context Summaries for Each Group"
    echo ""
    echo "🚀 RESULT: Complete trend visibility for proactive customer management!"
    echo ""
    echo "🔄 To test the comparative analysis:"
    echo "   python3 $NEW_SCRIPT"
else
    echo ""
    echo "⚠️ WARNING: Expected 10 cron jobs but found $CRON_COUNT"
    echo "Please check manually with: crontab -l"
fi 