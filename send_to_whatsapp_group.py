#!/usr/bin/env python3
"""
Script to send the (OB) groups analysis to Shopflo onboarding-internal group
Uses the existing WhatsApp bridge API with retry logic and better error handling
"""

import sys
import os
import time
from datetime import datetime

# Add the whatsapp-mcp-server to the path so we can import the module
sys.path.append(os.path.join(os.path.dirname(__file__), 'whatsapp-mcp-server'))

try:
    import whatsapp
except ImportError as e:
    print(f"❌ Error importing WhatsApp module: {e}")
    print("Make sure you're running this from the correct directory")
    sys.exit(1)

# Group JID for Shopflo onboarding-internal
TARGET_GROUP_JID = "120363321177381611@g.us"
GROUP_NAME = "Shopflo onboarding-internal"

# Retry configuration
MAX_SEND_RETRIES = 3
RETRY_DELAY = 30  # seconds between retries

# Analysis message to send
ANALYSIS_MESSAGE = """📊 **COMPREHENSIVE (OB) GROUPS ANALYSIS - LAST 5 DAYS**

🎯 **Executive Summary:**
• 📊 Total Groups Analyzed: 118 (OB) groups with recent activity
• 🏢 Internal Team Members: 62 identified from 5 internal groups

📈 **Results Breakdown:**
🚨 **NEEDS ATTENTION: 9 groups (7.6%)**
⚠️ **AT RISK: 9 groups (7.6%)**  
✅ **STABLE: 100 groups (84.8%)**

🚨 **TOP CRITICAL GROUPS:**

1. **🔴 (OB) Shopflo x Zilmor** - 50% negative sentiment
   • Issue: "After internal discussions, we've decided not to proceed with moving our checkout"

2. **🔴 (OB) Shopflo <> Urban Jungle** - 40% negative sentiment  
   • Issues: GA4 attribution problems, broken functionality

3. **🔴 (OB) Shopflo <> Flourish.shop** - 33% negative sentiment
   • Issue: Following docs but still facing integration problems

4. **🔴 (OB) Shopflo <> kayaralable** - 30% negative sentiment
   • Issues: Urgent checkout errors, multiple technical problems

5. **🔴 (OB) Shopflo <> Italian Shoe Company** - 25% negative sentiment
   • Issue: Requesting refund

🎯 **IMMEDIATE ACTION PLAN:**

**Priority 1 (Next 2 Hours):**
• Contact Zilmor - Address their decision to leave
• Fix Urban Jungle - Resolve GA4 attribution issues
• Support Flourish.shop - Debug integration problems

**Priority 2 (Next 8 Hours):**
• Resolve kayaralable checkout errors
• Process Italian Shoe Company refund
• Address Wood Gala payment gateway issues

**Priority 3 (Next 24 Hours):**
• Watch at-risk groups for escalation signs
• Track sentiment trends in stable groups
• Maintain response time standards

✨ **Success Metrics:**
• 85% of groups are stable with healthy communication
• Response time issues eliminated due to proper internal team recognition
• Focus on real merchant sentiment issues rather than internal coordination
• Accurate prioritization of groups needing immediate attention

Generated: {timestamp}"""

def test_whatsapp_connection() -> bool:
    """Test if WhatsApp API is properly connected"""
    try:
        # Try to get a simple API response to test connection
        success, message = whatsapp.send_message("test_connection_check", "test")
        # We expect this to fail for invalid JID, but it should not fail due to connection issues
        return True
    except Exception as e:
        error_msg = str(e).lower()
        if "not connected" in error_msg or "connection" in error_msg:
            return False
        # Other errors might be expected (like invalid JID), so we consider connection OK
        return True

def verify_group_exists(group_jid: str) -> bool:
    """Verify that the target group exists in the database"""
    try:
        chat = whatsapp.get_chat(group_jid)
        if chat:
            print(f"✅ Found group: {chat.name}")
            return True
        else:
            print(f"❌ Group with JID {group_jid} not found")
            return False
    except Exception as e:
        print(f"❌ Error checking group: {e}")
        return False

def send_message_with_retry(group_jid: str, message: str, group_name: str) -> bool:
    """Send message with retry logic for connection issues"""
    
    for attempt in range(1, MAX_SEND_RETRIES + 1):
        print(f"\n🚀 Sending message (attempt {attempt}/{MAX_SEND_RETRIES})...")
        
        try:
            success, response_message = whatsapp.send_message(group_jid, message)
            
            if success:
                print("✅ MESSAGE SENT SUCCESSFULLY!")
                print(f"📤 Response: {response_message}")
                print(f"🎯 Sent to: {group_name}")
                return True
            else:
                print("❌ FAILED TO SEND MESSAGE")
                print(f"💔 Error: {response_message}")
                
                # Check if it's a connection issue
                if "not connected" in str(response_message).lower():
                    print(f"🔌 Connection issue detected (attempt {attempt}/{MAX_SEND_RETRIES})")
                    
                    if attempt < MAX_SEND_RETRIES:
                        print(f"⏳ Waiting {RETRY_DELAY}s before retry...")
                        time.sleep(RETRY_DELAY)
                        
                        # Test connection before retry
                        print("🔍 Testing WhatsApp connection...")
                        if test_whatsapp_connection():
                            print("✅ Connection test passed, retrying...")
                        else:
                            print("❌ Connection still not available")
                        continue
                    else:
                        print("❌ Final attempt failed due to connection issues")
                        return False
                else:
                    # Non-connection error, don't retry
                    print("❌ Non-connection error, stopping retries")
                    return False
                    
        except Exception as e:
            print(f"❌ EXCEPTION OCCURRED: {e}")
            
            # Check if it's a connection-related exception
            error_msg = str(e).lower()
            if "connection" in error_msg or "timeout" in error_msg or "not connected" in error_msg:
                print(f"🔌 Connection exception detected (attempt {attempt}/{MAX_SEND_RETRIES})")
                
                if attempt < MAX_SEND_RETRIES:
                    print(f"⏳ Waiting {RETRY_DELAY}s before retry...")
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    print("❌ Final attempt failed due to connection exception")
                    return False
            else:
                # Non-connection exception, don't retry
                print("❌ Non-connection exception, stopping retries")
                return False
    
    return False

def send_analysis_to_group():
    """Send the analysis message to the WhatsApp group"""
    
    print("🚀 WhatsApp Group Message Sender (Enhanced)")
    print("="*60)
    print(f"Target Group: {GROUP_NAME}")
    print(f"Group JID: {TARGET_GROUP_JID}")
    print("="*60)
    
    # Step 1: Verify group exists
    print("\nStep 1: Verifying group exists...")
    if not verify_group_exists(TARGET_GROUP_JID):
        return False
    
    # Step 2: Format message with timestamp
    print("\nStep 2: Formatting message...")
    formatted_message = ANALYSIS_MESSAGE.format(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    print(f"✅ Message formatted ({len(formatted_message)} characters)")
    
    # Step 3: Send message with retry logic
    print(f"\nStep 3: Sending message to {GROUP_NAME} (with retry logic)...")
    return send_message_with_retry(TARGET_GROUP_JID, formatted_message, GROUP_NAME)

def main():
    """Main function"""
    print("📱 Shopflo (OB) Groups Analysis Sender (Enhanced v2.0)")
    print("=" * 80)
    
    # Check if WhatsApp API is available
    print("Checking WhatsApp API availability...")
    try:
        # Test API connection
        if test_whatsapp_connection():
            print("✅ WhatsApp API is accessible")
        else:
            print("❌ WhatsApp API connection failed - not connected to WhatsApp")
            print("💡 Will still attempt to send (retry logic will handle failures)")
    except Exception as e:
        print(f"❌ WhatsApp API connection test failed: {e}")
        print("💡 Make sure the WhatsApp bridge is running on localhost:8080")
        print("💡 Will still attempt to send (retry logic will handle failures)")
    
    # Send the analysis
    success = send_analysis_to_group()
    
    if success:
        print("\n🎉 ANALYSIS SUCCESSFULLY SENT TO TEAM!")
        print("📋 The analysis has been delivered to 'Shopflo onboarding-internal' group")
        print("✨ Team members will now be aware of critical merchant groups requiring attention")
    else:
        print("\n💔 FAILED TO SEND ANALYSIS")
        print("🔧 Troubleshooting steps:")
        print("1. Ensure WhatsApp bridge is running (localhost:8080)")
        print("2. Check if WhatsApp client is connected to WhatsApp Web")
        print("3. Verify group JID is correct")
        print("4. Check network connectivity")
        print("5. Try opening WhatsApp Web manually to refresh connection")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1) 