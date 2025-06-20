#!/usr/bin/env python3
"""
Script to send the (OB) groups analysis to Slack group
Based on the existing WhatsApp integration with retry logic and better error handling
"""

import sys
import os
import time
import json
import requests
from datetime import datetime
from typing import Dict, Any, Tuple

# Configuration
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL', None)  # Use webhook's default channel
MAX_SEND_RETRIES = 3
RETRY_DELAY = 30  # seconds between retries

# Import dynamic analysis
try:
    from dynamic_analysis import main as generate_dynamic_analysis
    DYNAMIC_ANALYSIS_AVAILABLE = True
except ImportError:
    print("⚠️ Dynamic analysis not available, falling back to static message")
    DYNAMIC_ANALYSIS_AVAILABLE = False

# Fallback static message (used if dynamic analysis fails)
FALLBACK_ANALYSIS_MESSAGE = """📊 **COMPREHENSIVE (OB) GROUPS ANALYSIS - LAST 5 DAYS**

⚠️ **USING FALLBACK ANALYSIS** - Dynamic analysis temporarily unavailable

🎯 **Executive Summary:**
• 📊 System monitoring active for (OB) groups
• 🏢 WhatsApp bridge operational
• 📅 Analysis system ready for real-time data

📈 **Status:**
🔄 **MONITORING: All groups being tracked**
⚠️ **NOTICE: Using fallback analysis mode**  
✅ **SYSTEM: Bridge and monitoring operational**

🎯 **IMMEDIATE ACTION:**
• Restore dynamic analysis capability
• Verify WhatsApp data access
• Check system dependencies

Generated: {timestamp}"""


def test_slack_connection() -> bool:
    """Test if Slack webhook is properly configured and accessible"""
    if not SLACK_WEBHOOK_URL:
        print("❌ SLACK_WEBHOOK_URL environment variable not set")
        return False
    
    try:
        # Send a test message to verify connection
        test_payload = {
            "text": "🔍 Connection test from WhatsApp Analysis System"
        }
        
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=test_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Slack connection test successful")
            return True
        else:
            print(f"❌ Slack connection test failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Slack connection test failed with exception: {e}")
        return False


def format_message_for_slack(message: str) -> Dict[str, Any]:
    """Format the analysis message for Slack with rich formatting"""
    
    # Convert markdown-style formatting to Slack format
    slack_message = message
    
    # Convert **bold** to *bold* for Slack
    import re
    slack_message = re.sub(r'\*\*(.*?)\*\*', r'*\1*', slack_message)
    
    # Create Slack-formatted payload with blocks for better formatting
    payload = {
        "username": "WhatsApp Analysis Bot",
        "icon_emoji": ":bar_chart:",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": slack_message
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📡 _Automated analysis from WhatsApp Bridge System_ • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            }
        ]
    }
    
    return payload


def send_to_slack_with_retry(message: str) -> bool:
    """Send message to Slack with retry logic for connection issues"""
    
    if not SLACK_WEBHOOK_URL:
        print("❌ SLACK_WEBHOOK_URL not configured")
        return False
    
    formatted_payload = format_message_for_slack(message)
    
    for attempt in range(1, MAX_SEND_RETRIES + 1):
        print(f"\n🚀 Sending message to Slack (attempt {attempt}/{MAX_SEND_RETRIES})...")
        
        try:
            response = requests.post(
                SLACK_WEBHOOK_URL,
                json=formatted_payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print("✅ MESSAGE SENT SUCCESSFULLY TO SLACK!")
                print(f"📤 Channel: {SLACK_CHANNEL if SLACK_CHANNEL else 'Default webhook channel'}")
                print(f"📊 Message length: {len(message)} characters")
                return True
            else:
                print("❌ FAILED TO SEND MESSAGE TO SLACK")
                print(f"💔 HTTP Status: {response.status_code}")
                print(f"💔 Response: {response.text}")
                
                # Check if it's a rate limit or temporary issue
                if response.status_code in [429, 500, 502, 503, 504]:
                    print(f"🔌 Temporary issue detected (attempt {attempt}/{MAX_SEND_RETRIES})")
                    
                    if attempt < MAX_SEND_RETRIES:
                        print(f"⏳ Waiting {RETRY_DELAY}s before retry...")
                        time.sleep(RETRY_DELAY)
                        continue
                    else:
                        print("❌ Final attempt failed due to temporary issues")
                        return False
                else:
                    # Client error, don't retry
                    print("❌ Client error, stopping retries")
                    return False
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ NETWORK EXCEPTION OCCURRED: {e}")
            
            # Check if it's a connection-related exception
            if attempt < MAX_SEND_RETRIES:
                print(f"🔌 Network exception detected (attempt {attempt}/{MAX_SEND_RETRIES})")
                print(f"⏳ Waiting {RETRY_DELAY}s before retry...")
                time.sleep(RETRY_DELAY)
                continue
            else:
                print("❌ Final attempt failed due to network exception")
                return False
        except Exception as e:
            print(f"❌ UNEXPECTED EXCEPTION: {e}")
            return False
    
    return False


def send_analysis_to_slack():
    """Send the analysis message to the Slack channel"""
    
    print("🚀 Slack Message Sender for WhatsApp Analysis")
    print("="*60)
    print(f"Target Channel: {SLACK_CHANNEL if SLACK_CHANNEL else 'Default webhook channel'}")
    print(f"Webhook URL: {SLACK_WEBHOOK_URL[:50]}..." if SLACK_WEBHOOK_URL else "❌ NOT SET")
    print("="*60)
    
    # Step 1: Verify Slack connection
    print("\nStep 1: Testing Slack connection...")
    if not test_slack_connection():
        print("❌ Slack connection failed. Please check your SLACK_WEBHOOK_URL.")
        return False
    
    # Step 2: Generate dynamic analysis or use fallback
    print("\nStep 2: Generating analysis message...")
    
    if DYNAMIC_ANALYSIS_AVAILABLE:
        try:
            print("🔄 Running dynamic analysis...")
            formatted_message = generate_dynamic_analysis()
            print("✅ Dynamic analysis generated successfully")
        except Exception as e:
            print(f"❌ Dynamic analysis failed: {e}")
            print("🔄 Falling back to static message...")
            formatted_message = FALLBACK_ANALYSIS_MESSAGE.format(
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
    else:
        print("⚠️ Using fallback analysis message...")
        formatted_message = FALLBACK_ANALYSIS_MESSAGE.format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    
    print(f"✅ Message formatted ({len(formatted_message)} characters)")
    
    # Step 3: Send message with retry logic
    print(f"\nStep 3: Sending message to Slack {SLACK_CHANNEL if SLACK_CHANNEL else 'default channel'} (with retry logic)...")
    return send_to_slack_with_retry(formatted_message)


def main():
    """Main function"""
    print("📊 Shopflo (OB) Groups Analysis - Slack Sender v1.0")
    print("=" * 80)
    
    # Check if Slack webhook is configured
    print("Checking Slack configuration...")
    if not SLACK_WEBHOOK_URL:
        print("❌ SLACK_WEBHOOK_URL environment variable not set!")
        print("💡 Set it with: export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...'")
        print("💡 Get your webhook URL from: https://api.slack.com/apps")
        sys.exit(1)
    
    print("✅ Slack webhook URL configured")
    
    # Send analysis to Slack
    success = send_analysis_to_slack()
    
    if success:
        print("\n" + "="*60)
        print("🎉 SUCCESS! Analysis sent to Slack successfully!")
        print("📊 Team can now view WhatsApp analysis in Slack")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ FAILED! Could not send analysis to Slack")
        print("🔧 Check logs above for troubleshooting")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    main() 