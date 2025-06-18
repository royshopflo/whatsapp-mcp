#!/usr/bin/env python3
"""
WhatsApp Bridge Health Check and Testing Tool
Tests the bridge functionality and monitors for database corruption
"""

import requests
import time
import sys
import subprocess
import sqlite3
from pathlib import Path

def test_database_health():
    """Check if databases are healthy"""
    store_dir = Path("whatsapp-bridge/store")
    whatsapp_db = store_dir / "whatsapp.db"
    messages_db = store_dir / "messages.db"
    
    print("🔍 Checking database health...")
    
    for db_path in [whatsapp_db, messages_db]:
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            result = cursor.execute("PRAGMA integrity_check").fetchone()
            conn.close()
            
            if result[0] == "ok":
                print(f"   ✅ {db_path.name}: OK")
            else:
                print(f"   ❌ {db_path.name}: CORRUPTED - {result[0]}")
                return False
        except Exception as e:
            print(f"   ❌ {db_path.name}: ERROR - {e}")
            return False
    
    return True

def test_bridge_api():
    """Test if the bridge API is responding"""
    print("🌐 Testing bridge API...")
    
    try:
        # Test API health endpoint
        response = requests.get("http://localhost:8080/", timeout=5)
        if response.status_code == 200:
            print("   ✅ API is responding")
            return True
        else:
            print(f"   ❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API (bridge may not be running)")
        return False
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
        return False

def test_message_sending():
    """Test message sending functionality"""
    print("📱 Testing message sending...")
    
    try:
        # Try to send a test message
        payload = {
            "recipient": "test",
            "message": "health_check"
        }
        
        response = requests.post(
            "http://localhost:8080/send",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("   ✅ Message sending successful")
                return True
            else:
                print(f"   ⚠️  Message sending failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Send API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Message sending test failed: {e}")
        return False

def is_bridge_running():
    """Check if the bridge process is running"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "whatsapp-bridge"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0 and result.stdout.strip()
    except:
        return False

def start_bridge():
    """Start the WhatsApp bridge"""
    print("🚀 Starting WhatsApp bridge...")
    
    try:
        # Start the bridge in the background
        subprocess.Popen(
            ["./start_whatsapp_bridge.sh"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait for it to start
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            if test_bridge_api():
                print("   ✅ Bridge started successfully")
                return True
            if i % 5 == 0:
                print(f"   ⏳ Waiting for bridge to start... ({i+1}s)")
        
        print("   ❌ Bridge failed to start within timeout")
        return False
        
    except Exception as e:
        print(f"   ❌ Failed to start bridge: {e}")
        return False

def monitor_bridge_health(duration_minutes=5):
    """Monitor bridge health for a specified duration"""
    print(f"🔍 Monitoring bridge health for {duration_minutes} minutes...")
    
    end_time = time.time() + (duration_minutes * 60)
    check_interval = 30  # Check every 30 seconds
    
    while time.time() < end_time:
        print(f"\n📊 Health check at {time.strftime('%H:%M:%S')}")
        
        # Check database health
        db_healthy = test_database_health()
        
        # Check API health
        api_healthy = test_bridge_api()
        
        if not db_healthy:
            print("🚨 DATABASE CORRUPTION DETECTED!")
            return False
        
        if not api_healthy:
            print("🚨 API IS DOWN!")
            return False
        
        print("   ✅ All systems healthy")
        time.sleep(check_interval)
    
    print(f"\n🎉 Bridge remained healthy for {duration_minutes} minutes!")
    return True

def main():
    """Main health check function"""
    print("🏥 WhatsApp Bridge Health Check Tool")
    print("=" * 50)
    
    # Check if bridge is running
    if not is_bridge_running():
        print("⚠️  Bridge is not running. Starting it...")
        if not start_bridge():
            print("❌ Failed to start bridge. Exiting.")
            return 1
    else:
        print("✅ Bridge is already running")
    
    # Run initial health checks
    print("\n🔍 Running initial health checks...")
    
    db_healthy = test_database_health()
    api_healthy = test_bridge_api()
    
    if not db_healthy:
        print("\n❌ Database issues detected. Run the database recovery script first.")
        return 1
    
    if not api_healthy:
        print("\n❌ API issues detected. Check bridge logs.")
        return 1
    
    print("\n✅ Initial health checks passed!")
    
    # Test message sending
    test_message_sending()
    
    # Ask user if they want to monitor
    try:
        duration = int(input("\nEnter monitoring duration in minutes (0 to skip): "))
        if duration > 0:
            success = monitor_bridge_health(duration)
            return 0 if success else 1
    except (ValueError, KeyboardInterrupt):
        print("\nSkipping monitoring.")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Health check interrupted by user")
        sys.exit(1) 