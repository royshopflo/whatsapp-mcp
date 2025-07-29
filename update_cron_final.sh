#!/bin/bash

# Final Cron Jobs Update - Complete Internal Groups List
# Excludes ALL internal groups from critical customer alerts

SCRIPT_DIR="/Users/macbook/whatsapp-mcp-3"
ANALYSIS_SCRIPT="$SCRIPT_DIR/send_analysis_to_priority_group_fixed.py"
LOG_DIR="$SCRIPT_DIR/logs"

echo "🔄 FINAL Cron Jobs Update - Complete Internal Groups"
echo "======================================================================"
echo "📋 Internal Groups Excluded from Critical Customer Alerts:"
echo "• Solutions War Room - Internal technical issue resolution team"
echo "• Shopflo war room - Internal operational issues team"
echo "• Priority inbox check - Internal priority notifications group"
echo "• Shopflo customer success - Internal customer success team"
echo "• Shopflo - onboarding - Internal client onboarding team"
echo "• Shopflo Sales<>CS - Internal sales & customer success coordination"
echo ""
echo "✅ ONLY Customer groups (Emma, BornGood, Boult, etc.) trigger critical alerts"
echo "======================================================================"

# Backup current crontab
echo "📋 Backing up current crontab..."
BACKUP_FILE="$SCRIPT_DIR/crontab_backup_final_$(date +%Y%m%d_%H%M%S).txt"
crontab -l > "$BACKUP_FILE" 2>/dev/null || echo "# No existing crontab" > "$BACKUP_FILE"
echo "✅ Crontab backed up to: $BACKUP_FILE"

# Create temporary cron file
TEMP_CRON=$(mktemp)

# Add existing cron jobs (excluding priority analysis jobs)
crontab -l 2>/dev/null | grep -v "send_analysis_to_priority_group" > "$TEMP_CRON" || true

# Add final priority analysis cron jobs
echo "" >> "$TEMP_CRON"
echo "# Priority Analysis WhatsApp Notifications - FINAL with ALL Internal Groups Excluded" >> "$TEMP_CRON"
echo "0 10 * * * cd $SCRIPT_DIR && /usr/bin/python3 $ANALYSIS_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 11 * * * cd $SCRIPT_DIR && /usr/bin/python3 $ANALYSIS_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 12 * * * cd $SCRIPT_DIR && /usr/bin/python3 $ANALYSIS_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 13 * * * cd $SCRIPT_DIR && /usr/bin/python3 $ANALYSIS_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 14 * * * cd $SCRIPT_DIR && /usr/bin/python3 $ANALYSIS_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 15 * * * cd $SCRIPT_DIR && /usr/bin/python3 $ANALYSIS_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 16 * * * cd $SCRIPT_DIR && /usr/bin/python3 $ANALYSIS_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 17 * * * cd $SCRIPT_DIR && /usr/bin/python3 $ANALYSIS_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 18 * * * cd $SCRIPT_DIR && /usr/bin/python3 $ANALYSIS_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"
echo "0 19 * * * cd $SCRIPT_DIR && /usr/bin/python3 $ANALYSIS_SCRIPT >> $LOG_DIR/priority_analysis_\$(date +\%Y\%m\%d).log 2>&1" >> "$TEMP_CRON"

# Install the updated crontab
echo "📝 Installing final crontab with complete internal groups exclusion..."
crontab "$TEMP_CRON"

# Cleanup
rm "$TEMP_CRON"

echo "✅ Final cron jobs successfully updated!"
echo ""
echo "🎯 **FINAL ALERT SYSTEM:**"
echo ""
echo "🚨 **CRITICAL CUSTOMER ALERTS** (Immediate Action Required):"
echo "• Shopflo <> Emma - E-commerce merchant client"
echo "• BornGood || Shopflow - Health & wellness brand customer"
echo "• Boult / Shopflo - Audio accessories brand customer"
echo "• Traya || Easebuzz - Hair care brand with payment integration"
echo "• Renee Cosmetics<>Appmaker - Beauty brand with app development"
echo "• NaturUp<>shopflo - Natural products merchant"
echo "• Shopflo<> Tribal Veda - Ayurvedic brand customer"
echo "• Shopflo <> Traya.health - Healthcare brand customer"
echo ""
echo "🤝 **PARTNER MONITORING** (Tracked but not critical customer alerts):"
echo "• All integration partners (Indulgeo, Sirevest, Cai Store, etc.)"
echo ""
echo "🏠 **INTERNAL WORKFLOW AWARENESS** (No critical customer alerts):"
echo "• Solutions War Room ✅"
echo "• Shopflo war room ✅"
echo "• Priority inbox check ✅"
echo "• Shopflo customer success ✅"
echo "• Shopflo - onboarding ✅"
echo "• Shopflo Sales<>CS ✅"
echo ""
echo "📁 Logs: $LOG_DIR/priority_analysis_YYYYMMDD.log"

# Verify cron installation
echo ""
echo "🔍 Final verification..."
CRON_COUNT=$(crontab -l | grep -c "send_analysis_to_priority_group_fixed.py" || true)
echo "✅ Found $CRON_COUNT priority analysis cron jobs installed"

if [ "$CRON_COUNT" -eq 10 ]; then
    echo ""
    echo "🎉 PERFECT! All 10 final analysis cron jobs installed successfully."
    echo ""
    echo "📱 Priority inbox check group will now receive smart analysis that:"
    echo "• ✅ ONLY triggers critical alerts for CUSTOMER issues"
    echo "• ✅ Tracks partner activity without critical alerts"
    echo "• ✅ Shows internal team activity for awareness only"
    echo "• ✅ Provides group summaries for business context"
    echo "• ✅ Delivers hourly updates from 10 AM to 7 PM"
    echo ""
    echo "🔥 RESULT: Clean customer-focused alerts, no internal noise!"
else
    echo ""
    echo "⚠️ WARNING: Expected 10 cron jobs but found $CRON_COUNT"
    echo "Please check manually with: crontab -l"
fi 