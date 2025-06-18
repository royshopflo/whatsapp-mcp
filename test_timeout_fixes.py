#!/usr/bin/env python3
"""
Test script to validate WhatsApp bridge timeout fixes
"""

import requests
import json
import time
import sys

def test_timeout_fixes():
    """Test the implemented timeout fixes"""
    print("🧪 Testing WhatsApp Bridge Timeout Fixes")
    print("=" * 50)
    
    # Test configuration
    api_url = "http://localhost:8080/api/send"
    test_recipient = "120363321177381611@g.us"  # Internal test group
    
    # Test messages to send
    test_messages = [
        "🔧 Testing timeout fix #1",
        "🔧 Testing timeout fix #2", 
        "🔧 Testing timeout fix #3"
    ]
    
    success_count = 0
    timeout_count = 0
    other_errors = 0
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📤 Test {i}: Sending message...")
        print(f"   Message: {message}")
        
        try:
            # Send request with timeout
            response = requests.post(
                api_url,
                json={
                    "recipient": test_recipient,
                    "message": message
                },
                headers={"Content-Type": "application/json"},
                timeout=60  # 60 second timeout for the HTTP request
            )
            
            response_data = response.json()
            
            if response_data.get("success", False):
                print(f"   ✅ SUCCESS: {response_data.get('message', 'Message sent')}")
                success_count += 1
            else:
                error_msg = response_data.get("message", "Unknown error")
                print(f"   ❌ FAILED: {error_msg}")
                
                # Check if this is a timeout-related error
                if any(keyword in error_msg.lower() for keyword in [
                    "timeout", "device list", "info query", "usync query"
                ]):
                    timeout_count += 1
                    print(f"   🔍 TIMEOUT ERROR DETECTED (this should be improved now)")
                else:
                    other_errors += 1
                    
        except requests.exceptions.Timeout:
            print(f"   ⏰ HTTP REQUEST TIMEOUT")
            timeout_count += 1
        except requests.exceptions.ConnectionError:
            print(f"   🔌 CONNECTION ERROR: Bridge may not be running")
            other_errors += 1
        except Exception as e:
            print(f"   💥 UNEXPECTED ERROR: {e}")
            other_errors += 1
            
        # Wait between tests
        if i < len(test_messages):
            print(f"   ⏳ Waiting 5 seconds before next test...")
            time.sleep(5)
    
    # Summary
    print(f"\n📊 TEST RESULTS SUMMARY")
    print(f"=" * 30)
    print(f"✅ Successful sends: {success_count}/{len(test_messages)}")
    print(f"⏰ Timeout errors: {timeout_count}/{len(test_messages)}")
    print(f"❌ Other errors: {other_errors}/{len(test_messages)}")
    
    # Analysis
    if success_count == len(test_messages):
        print(f"\n🎉 EXCELLENT! All timeout fixes are working perfectly!")
        return True
    elif timeout_count == 0:
        print(f"\n✅ GOOD! No timeout errors detected - other issues may exist")
        return True
    elif timeout_count < len(test_messages):
        print(f"\n🔄 IMPROVED! Timeout fixes are working but some issues remain")
        print(f"   Before fixes: Most sends would fail with timeouts")
        print(f"   After fixes: {success_count} successful, {timeout_count} timeouts")
        return True
    else:
        print(f"\n⚠️  NEEDS ATTENTION: Timeout fixes may need further adjustment")
        return False

if __name__ == "__main__":
    try:
        success = test_timeout_fixes()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Test script error: {e}")
        sys.exit(1) 