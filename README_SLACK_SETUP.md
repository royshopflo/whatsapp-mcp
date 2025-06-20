# 📊 Slack Integration for WhatsApp Analysis

## 🚀 Overview

This Slack integration allows you to automatically send your WhatsApp group analysis reports to a Slack channel, complementing or replacing the existing WhatsApp notifications.

## 📋 Prerequisites

1. **Slack Workspace Access** - Admin permissions to create webhook integrations
2. **WhatsApp Bridge Running** - The existing WhatsApp bridge system on `localhost:8080`
3. **Python Environment** - Python 3.7+ with `requests` package

## 🔧 Setup Instructions

### Step 1: Create Slack Webhook

1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Click **"Create New App"** → **"From scratch"**
3. Name your app (e.g., "WhatsApp Analysis Bot")
4. Select your workspace
5. Go to **"Incoming Webhooks"** in the sidebar
6. Toggle **"Activate Incoming Webhooks"** to ON
7. Click **"Add New Webhook to Workspace"**
8. Select the channel where you want to receive reports
9. Click **"Allow"**
10. Copy the webhook URL (starts with `https://hooks.slack.com/services/`)

### Step 2: Configure Environment

```bash
# Set the Slack webhook URL
export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

# Optional: Set custom channel (default: #whatsapp-analysis)
export SLACK_CHANNEL='#your-channel-name'

# Make it permanent by adding to your shell profile
echo 'export SLACK_WEBHOOK_URL="your_webhook_url"' >> ~/.bashrc
# or for zsh users:
echo 'export SLACK_WEBHOOK_URL="your_webhook_url"' >> ~/.zshrc
```

### Step 3: Install and Test

```bash
# Install required packages
pip install requests pytest

# Test the integration
python test_slack_integration.py

# Manual test run
python send_to_slack_group.py
```

### Step 4: Setup Automated Cron Jobs

```bash
# Run the interactive setup
./setup_slack_cron.sh
```

The setup script will:
- Test your Slack configuration
- Let you choose a schedule (same as WhatsApp, 3x daily, or custom)
- Configure cron jobs automatically
- Create log directories

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `send_to_slack_group.py` | Main Python script for sending to Slack |
| `automated_slack_analysis.sh` | Bash wrapper for cron execution |
| `setup_slack_cron.sh` | Interactive setup for cron jobs |
| `test_slack_integration.py` | Test suite for validation |
| `README_SLACK_SETUP.md` | This documentation file |

## 🔄 How It Works

### Analysis Generation
1. **Data Source**: Uses the same dynamic analysis system as WhatsApp integration
2. **Fallback**: If dynamic analysis fails, sends a status message
3. **Formatting**: Converts markdown formatting to Slack-compatible format

### Message Delivery
1. **Retry Logic**: 3 attempts with 30-second delays for network issues
2. **Error Handling**: Distinguishes between temporary and permanent failures
3. **Logging**: Comprehensive logs in `logs/slack_analysis_YYYYMMDD.log`

### Schedule Options
- **Option 1**: Same as WhatsApp (6x daily: 10AM, 11AM, 12PM, 2PM, 4PM, 6PM)
- **Option 2**: Reduced frequency (3x daily: 10AM, 2PM, 6PM)
- **Option 3**: Custom schedule using cron syntax

## 📊 Message Format

Messages are sent with rich Slack formatting:

```
📊 **COMPREHENSIVE (OB) GROUPS ANALYSIS - LAST 5 DAYS**

🎯 **Executive Summary:**
• Analysis results and insights
• Group health status
• Action items

📈 **Detailed Findings:**
🚨 **Needs Attention**: [Count] groups
⚠️ **At Risk**: [Count] groups  
✅ **Stable**: [Count] groups

Generated: 2024-01-01 10:00:00
```

## 🛠️ Management Commands

### View Logs
```bash
# Today's log
cat logs/slack_analysis_$(date +%Y%m%d).log

# Real-time monitoring
tail -f logs/slack_analysis_$(date +%Y%m%d).log
```

### Manual Execution
```bash
# Test single run
./automated_slack_analysis.sh

# Direct Python execution
python send_to_slack_group.py
```

### Cron Management
```bash
# View current jobs
crontab -l | grep slack

# Edit schedule
crontab -e

# Remove Slack automation
crontab -l | grep -v automated_slack_analysis | crontab -
```

### Troubleshooting
```bash
# Test Slack connection
python3 -c "
import os, requests
url = os.getenv('SLACK_WEBHOOK_URL')
resp = requests.post(url, json={'text': 'Test message'})
print(f'Status: {resp.status_code}')
"

# Check webhook URL format
echo $SLACK_WEBHOOK_URL

# Verify script permissions
ls -la automated_slack_analysis.sh send_to_slack_group.py
```

## 🚨 Common Issues & Solutions

### Issue: "SLACK_WEBHOOK_URL not set"
**Solution**: 
```bash
export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...'
# Add to ~/.bashrc or ~/.zshrc for persistence
```

### Issue: "HTTP 404" from Slack
**Causes**: 
- Webhook URL is incorrect
- App was deleted from Slack workspace
- Webhook was revoked

**Solution**: Recreate webhook in Slack API console

### Issue: "HTTP 403" from Slack
**Causes**:
- App lacks permissions
- Channel doesn't exist
- Workspace settings block external apps

**Solution**: Check app permissions and workspace settings

### Issue: Messages not appearing
**Causes**:
- Wrong channel specified
- Channel is archived
- App not added to private channel

**Solution**: Verify channel exists and app has access

### Issue: Cron jobs not running
**Causes**:
- Environment variables not available in cron
- Script path issues
- Permission problems

**Solution**: Use absolute paths and check cron logs

## 📈 Integration with Existing System

### Dual Delivery (WhatsApp + Slack)
To send to both WhatsApp and Slack:

1. Keep existing WhatsApp cron jobs
2. Add Slack cron jobs with same schedule
3. Both will use the same dynamic analysis

### Migration from WhatsApp
To replace WhatsApp with Slack:

1. Setup Slack integration
2. Test thoroughly
3. Remove WhatsApp cron jobs:
   ```bash
   crontab -l | grep -v automated_analysis.sh | crontab -
   ```

### Custom Integration
To modify the analysis or formatting:

1. Edit `send_to_slack_group.py`
2. Modify the `format_message_for_slack()` function
3. Test with `python send_to_slack_group.py`

## 🔒 Security Considerations

1. **Webhook URLs**: Treat as secrets, don't commit to version control
2. **Environment Variables**: Use proper shell configuration
3. **Log Files**: May contain sensitive analysis data
4. **Network Traffic**: HTTPS encrypted to Slack

## 📞 Support & Troubleshooting

### Debug Mode
Run with verbose output:
```bash
SLACK_WEBHOOK_URL='your_url' python -v send_to_slack_group.py
```

### Log Analysis
```bash
# Check for errors in logs
grep -i error logs/slack_analysis_*.log

# Check success rate
grep -c "SUCCESS" logs/slack_analysis_*.log
```

### Manual Testing
```bash
# Test with custom message
python3 -c "
from send_to_slack_group import send_to_slack_with_retry
result = send_to_slack_with_retry('🧪 Manual test message')
print(f'Result: {result}')
"
```

---

**🎉 Your WhatsApp analysis is now integrated with Slack!**

The team will receive automated reports in Slack, enabling better visibility and faster response times to merchant concerns. 