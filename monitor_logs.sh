#!/bin/bash

# Monitor WhatsApp Analysis Logs and CRON Status

SCRIPT_DIR="/Users/macbook/whatsapp-mcp-2"
LOG_DIR="$SCRIPT_DIR/logs"
TODAY=$(date +%Y%m%d)
LOG_FILE="$LOG_DIR/analysis_$TODAY.log"

show_menu() {
    echo ""
    echo "📊 WhatsApp Analysis Monitor"
    echo "============================"
    echo "1. View today's log"
    echo "2. Tail live log (follow)"
    echo "3. Check cron job status"
    echo "4. View recent analysis runs"
    echo "5. Test run analysis manually"
    echo "6. Remove cron job"
    echo "0. Exit"
    echo ""
    read -p "Choose an option [0-6]: " choice
}

view_todays_log() {
    if [ -f "$LOG_FILE" ]; then
        echo "📋 Today's log file: $LOG_FILE"
        echo "==============================================="
        cat "$LOG_FILE"
    else
        echo "❌ No log file found for today: $LOG_FILE"
    fi
}

tail_live_log() {
    if [ -f "$LOG_FILE" ]; then
        echo "📈 Following live log: $LOG_FILE"
        echo "Press Ctrl+C to stop"
        echo "==============================================="
        tail -f "$LOG_FILE"
    else
        echo "❌ No log file found for today: $LOG_FILE"
        echo "💡 The log file will be created when the analysis runs"
    fi
}

check_cron_status() {
    echo "📅 Current CRON jobs:"
    echo "===================="
    crontab -l | grep -A 10 -B 2 "WhatsApp Analysis" || echo "❌ No WhatsApp Analysis cron jobs found"
    echo ""
    echo "🕐 Next scheduled runs:"
    echo "======================"
    echo "Today: $(date '+%Y-%m-%d')"
    echo "- 10:00 AM IST"
    echo "- 02:00 PM IST" 
    echo "- 06:00 PM IST"
    echo ""
    echo "Current time: $(date '+%H:%M %Z')"
}

view_recent_runs() {
    echo "📊 Recent Analysis Runs:"
    echo "======================="
    
    # Find all log files in the last 7 days
    find "$LOG_DIR" -name "analysis_*.log" -mtime -7 2>/dev/null | sort | while read logfile; do
        if [ -f "$logfile" ]; then
            echo ""
            echo "📅 $(basename "$logfile" .log | sed 's/analysis_//'):"
            grep -E "(SUCCESS|FAILED)" "$logfile" | tail -3
        fi
    done
    
    if [ ! -d "$LOG_DIR" ] || [ -z "$(ls -A "$LOG_DIR" 2>/dev/null)" ]; then
        echo "❌ No log files found in $LOG_DIR"
    fi
}

test_manual_run() {
    echo "🚀 Running manual analysis test..."
    echo "================================="
    "$SCRIPT_DIR/automated_analysis.sh"
    echo ""
    echo "✅ Manual run completed. Check the output above for results."
}

remove_cron_job() {
    echo "⚠️  Removing WhatsApp Analysis cron jobs..."
    echo "=========================================="
    
    # Backup current crontab
    crontab -l > "$SCRIPT_DIR/crontab_backup_removal_$(date +%Y%m%d_%H%M%S).txt" 2>/dev/null
    
    # Remove WhatsApp Analysis cron jobs
    crontab -l 2>/dev/null | grep -v "WhatsApp Analysis" | grep -v "automated_analysis.sh" | crontab -
    
    echo "✅ CRON jobs removed successfully"
    echo "📋 Backup saved to: $SCRIPT_DIR/crontab_backup_removal_$(date +%Y%m%d_%H%M%S).txt"
    echo ""
    echo "📅 Current crontab:"
    crontab -l || echo "No cron jobs remaining"
}

# Main loop
while true; do
    show_menu
    
    case $choice in
        1)
            view_todays_log
            read -p "Press Enter to continue..."
            ;;
        2)
            tail_live_log
            ;;
        3)
            check_cron_status
            read -p "Press Enter to continue..."
            ;;
        4)
            view_recent_runs
            read -p "Press Enter to continue..."
            ;;
        5)
            test_manual_run
            read -p "Press Enter to continue..."
            ;;
        6)
            read -p "Are you sure you want to remove the cron job? (y/N): " confirm
            if [[ $confirm =~ ^[Yy]$ ]]; then
                remove_cron_job
            else
                echo "Operation cancelled"
            fi
            read -p "Press Enter to continue..."
            ;;
        0)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please choose 0-6."
            read -p "Press Enter to continue..."
            ;;
    esac
done 