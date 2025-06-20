#!/usr/bin/env python3
"""
Demo script for Slack integration
Shows how the system works without requiring actual Slack credentials
"""

import json
from datetime import datetime
from send_to_slack_group import format_message_for_slack, FALLBACK_ANALYSIS_MESSAGE

def demo_slack_integration():
    """Demonstrate the Slack integration without actually sending messages"""
    
    print("🚀 Slack Integration Demo")
    print("=" * 60)
    print()
    
    # Show the message that would be sent
    print("📊 Sample Analysis Message:")
    print("-" * 40)
    
    # Use the fallback message as demo content
    demo_message = FALLBACK_ANALYSIS_MESSAGE.format(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    
    print(demo_message)
    print()
    
    # Show how it gets formatted for Slack
    print("📱 Formatted for Slack:")
    print("-" * 40)
    
    slack_payload = format_message_for_slack(demo_message)
    
    # Pretty print the JSON payload
    print(json.dumps(slack_payload, indent=2, ensure_ascii=False))
    print()
    
    # Show configuration info
    print("⚙️ Configuration Required:")
    print("-" * 40)
    print("Environment Variables:")
    print("• SLACK_WEBHOOK_URL - Your Slack webhook URL")
    print("• SLACK_CHANNEL (optional) - Target channel (default: #whatsapp-analysis)")
    print()
    
    print("🔧 Setup Commands:")
    print("-" * 40)
    print("1. export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...'")
    print("2. ./setup_slack_cron.sh")
    print("3. python send_to_slack_group.py  # Test run")
    print()
    
    print("📅 Scheduling Options:")
    print("-" * 40)
    print("• Same as WhatsApp: 6x daily (10AM, 11AM, 12PM, 2PM, 4PM, 6PM)")
    print("• Reduced frequency: 3x daily (10AM, 2PM, 6PM)")
    print("• Custom schedule using cron syntax")
    print()
    
    print("✅ Benefits:")
    print("-" * 40)
    print("• Native Slack formatting with rich blocks")
    print("• Retry logic for network issues")
    print("• Comprehensive logging")
    print("• Same analysis data as WhatsApp version")
    print("• Easy integration with existing workflow")
    print()
    
    print("🎉 Ready to set up? Run: ./setup_slack_cron.sh")

if __name__ == "__main__":
    demo_slack_integration() 