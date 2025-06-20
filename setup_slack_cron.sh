#!/bin/bash

# 🚀 Setup Slack CRON Job for Automated WhatsApp Analysis
# Similar to setup_cron.sh but for Slack integration

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTOMATION_SCRIPT="$SCRIPT_DIR/automated_slack_analysis.sh"
LOG_DIR="$SCRIPT_DIR/logs"

# Helper functions
print_header() {
    echo -e "${BLUE}=========================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=========================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Main setup function
main() {
    print_header "SLACK AUTOMATION SETUP"
    
    echo "Setting up automated WhatsApp analysis delivery to Slack..."
    echo "This will create cron jobs to send analysis reports to your Slack channel."
    echo ""
    
    # Check if Slack webhook URL is configured
    if [ -z "$SLACK_WEBHOOK_URL" ]; then
        print_error "SLACK_WEBHOOK_URL environment variable not set!"
        echo ""
        echo "To get your Slack webhook URL:"
        echo "1. Go to https://api.slack.com/apps"
        echo "2. Create a new app or select existing app"
        echo "3. Go to 'Incoming Webhooks' and activate it"
        echo "4. Click 'Add New Webhook to Workspace'"
        echo "5. Select the channel and authorize"
        echo "6. Copy the webhook URL"
        echo ""
        echo "Then set it with:"
        echo "export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...'"
        echo ""
        echo "You can also add it to your ~/.bashrc or ~/.zshrc:"
        echo "echo 'export SLACK_WEBHOOK_URL=\"your_webhook_url\"' >> ~/.bashrc"
        echo ""
        exit 1
    fi
    
    print_success "SLACK_WEBHOOK_URL is configured"
    
    # Create logs directory
    if [ ! -d "$LOG_DIR" ]; then
        mkdir -p "$LOG_DIR"
        print_success "Created logs directory: $LOG_DIR"
    else
        print_info "Logs directory already exists: $LOG_DIR"
    fi
    
    # Make automation script executable
    if [ -f "$AUTOMATION_SCRIPT" ]; then
        chmod +x "$AUTOMATION_SCRIPT"
        print_success "Made automation script executable"
    else
        print_error "Automation script not found: $AUTOMATION_SCRIPT"
        exit 1
    fi
    
    # Make Python script executable
    PYTHON_SCRIPT="$SCRIPT_DIR/send_to_slack_group.py"
    if [ -f "$PYTHON_SCRIPT" ]; then
        chmod +x "$PYTHON_SCRIPT"
        print_success "Made Python script executable"
    else
        print_error "Python script not found: $PYTHON_SCRIPT"
        exit 1
    fi
    
    # Test the integration before setting up cron
    print_info "Testing Slack integration..."
    echo ""
    
    # Test connection first
    python3 -c "
import os, requests, sys
webhook_url = os.getenv('SLACK_WEBHOOK_URL')
if not webhook_url:
    print('❌ SLACK_WEBHOOK_URL not found')
    sys.exit(1)

try:
    response = requests.post(webhook_url, json={'text': '🧪 Test from WhatsApp Analysis Setup'}, timeout=10)
    if response.status_code == 200:
        print('✅ Slack connection test successful!')
    else:
        print(f'❌ Slack test failed: HTTP {response.status_code}')
        sys.exit(1)
except Exception as e:
    print(f'❌ Slack test failed: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_success "Slack integration test passed"
    else
        print_error "Slack integration test failed"
        print_warning "Please check your SLACK_WEBHOOK_URL and try again"
        exit 1
    fi
    
    echo ""
    print_header "CRON SCHEDULE SETUP"
    
    # Ask user for schedule preference
    echo "Choose your preferred schedule:"
    echo "1. Same as WhatsApp (6 times daily: 10AM, 11AM, 12PM, 2PM, 4PM, 6PM)"
    echo "2. 3 times daily (10AM, 2PM, 6PM)"
    echo "3. Custom schedule"
    echo ""
    read -p "Enter your choice (1-3): " schedule_choice
    
    case $schedule_choice in
        1)
            CRON_ENTRIES=(
                "0 10 * * * $AUTOMATION_SCRIPT >/dev/null 2>&1"
                "0 11 * * * $AUTOMATION_SCRIPT >/dev/null 2>&1"
                "0 12 * * * $AUTOMATION_SCRIPT >/dev/null 2>&1"
                "0 14 * * * $AUTOMATION_SCRIPT >/dev/null 2>&1"
                "0 16 * * * $AUTOMATION_SCRIPT >/dev/null 2>&1"
                "0 18 * * * $AUTOMATION_SCRIPT >/dev/null 2>&1"
            )
            SCHEDULE_DESC="6 times daily (10AM, 11AM, 12PM, 2PM, 4PM, 6PM)"
            ;;
        2)
            CRON_ENTRIES=(
                "0 10 * * * $AUTOMATION_SCRIPT >/dev/null 2>&1"
                "0 14 * * * $AUTOMATION_SCRIPT >/dev/null 2>&1"
                "0 18 * * * $AUTOMATION_SCRIPT >/dev/null 2>&1"
            )
            SCHEDULE_DESC="3 times daily (10AM, 2PM, 6PM)"
            ;;
        3)
            echo ""
            echo "Enter custom cron schedule (format: minute hour * * *)"
            echo "Examples:"
            echo "  0 9 * * *    (Daily at 9 AM)"
            echo "  0 */4 * * *  (Every 4 hours)"
            echo "  0 9,17 * * * (9 AM and 5 PM daily)"
            echo ""
            read -p "Enter cron schedule: " custom_schedule
            CRON_ENTRIES=("$custom_schedule $AUTOMATION_SCRIPT >/dev/null 2>&1")
            SCHEDULE_DESC="Custom: $custom_schedule"
            ;;
        *)
            print_error "Invalid choice. Exiting."
            exit 1
            ;;
    esac
    
    # Backup existing crontab
    BACKUP_FILE="$SCRIPT_DIR/crontab_backup_slack_$(date +%Y%m%d_%H%M%S).txt"
    crontab -l > "$BACKUP_FILE" 2>/dev/null
    print_success "Backed up existing crontab to: $BACKUP_FILE"
    
    # Add new cron entries
    echo ""
    print_info "Adding cron entries..."
    
    # Get current crontab and add our entries
    (crontab -l 2>/dev/null; echo ""; echo "# Slack WhatsApp Analysis - Auto-send to Slack channel") | crontab -
    
    for entry in "${CRON_ENTRIES[@]}"; do
        (crontab -l 2>/dev/null; echo "$entry") | crontab -
        print_success "Added: $entry"
    done
    
    echo ""
    print_header "SETUP COMPLETE!"
    
    print_success "Slack automation is now configured!"
    echo ""
    echo "📊 Schedule: $SCHEDULE_DESC"
    echo "📱 Target: Slack channel configured in webhook"
    echo "📝 Logs: $LOG_DIR/slack_analysis_YYYYMMDD.log"
    echo ""
    
    # Show current cron jobs
    print_info "Current cron jobs:"
    crontab -l | grep -E "(slack|Slack)" || echo "No Slack-related cron jobs found"
    
    echo ""
    print_info "Management commands:"
    echo "• View logs: cat logs/slack_analysis_\$(date +%Y%m%d).log"
    echo "• Test manual run: ./automated_slack_analysis.sh"
    echo "• Edit cron: crontab -e"
    echo "• Remove cron: crontab -l | grep -v automated_slack_analysis | crontab -"
    
    echo ""
    print_success "🎉 Your team will now receive WhatsApp analysis in Slack!"
}

# Run main function
main "$@" 