#!/bin/bash

# Quick test script for Slack webhook
echo "🧪 Testing Slack Webhook Configuration"
echo "======================================"

if [ -z "$SLACK_WEBHOOK_URL" ]; then
    echo "❌ SLACK_WEBHOOK_URL not set!"
    echo ""
    echo "Please set it first:"
    echo "export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...'"
    echo ""
    echo "To get your webhook URL:"
    echo "1. Go to https://api.slack.com/apps"
    echo "2. Create new app → Incoming Webhooks"
    echo "3. Add webhook to workspace"
    echo "4. Copy the URL"
    exit 1
fi

echo "✅ SLACK_WEBHOOK_URL is set"
echo "URL: ${SLACK_WEBHOOK_URL:0:50}..."
echo ""

echo "🚀 Sending test message..."

python3 -c "
import requests, os, sys
webhook_url = os.getenv('SLACK_WEBHOOK_URL')
try:
    response = requests.post(webhook_url, json={
        'text': '🧪 Test message from WhatsApp Analysis System - Setup is working!',
        'username': 'WhatsApp Analysis Bot',
        'icon_emoji': ':bar_chart:'
    }, timeout=10)
    
    if response.status_code == 200:
        print('✅ SUCCESS! Test message sent to Slack')
        print('📱 Check your Slack channel for the test message')
    else:
        print(f'❌ Failed: HTTP {response.status_code}')
        print(f'Response: {response.text}')
        sys.exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Slack integration is working!"
    echo "Now you can run: ./setup_slack_cron.sh"
else
    echo ""
    echo "❌ Test failed. Please check your webhook URL."
fi 