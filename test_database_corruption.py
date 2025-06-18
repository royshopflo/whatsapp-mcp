#!/usr/bin/env python3
"""
Database Corruption Diagnostic Tool
This script tests the integrity of the WhatsApp bridge SQLite databases
"""

import sqlite3
import os
import sys
from pathlib import Path

def test_database_integrity(db_path):
    """Test the integrity of a SQLite database"""
    print(f"\n=== Testing database: {db_path} ===")
    
    if not os.path.exists(db_path):
        print(f"❌ Database file does not exist: {db_path}")
        return False
    
    try:
        # Check file permissions
        stat_info = os.stat(db_path)
        print(f"📊 File size: {stat_info.st_size / (1024*1024):.2f} MB")
        print(f"🔐 File permissions: {oct(stat_info.st_mode)[-3:]}")
        
        # Try to open database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Run integrity check
        print("🔍 Running PRAGMA integrity_check...")
        result = cursor.execute("PRAGMA integrity_check").fetchone()
        
        if result[0] == "ok":
            print("✅ Database integrity check: PASSED")
            integrity_ok = True
        else:
            print(f"❌ Database integrity check: FAILED - {result[0]}")
            integrity_ok = False
        
        # Run quick check
        print("🔍 Running PRAGMA quick_check...")
        result = cursor.execute("PRAGMA quick_check").fetchone()
        
        if result[0] == "ok":
            print("✅ Database quick check: PASSED")
            quick_ok = True
        else:
            print(f"❌ Database quick check: FAILED - {result[0]}")
            quick_ok = False
        
        # Check database schema
        print("📋 Checking database schema...")
        tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        print(f"📊 Found {len(tables)} tables: {[t[0] for t in tables]}")
        
        # Try to count rows in each table
        for table in tables:
            try:
                count = cursor.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
                print(f"   {table[0]}: {count} rows")
            except Exception as e:
                print(f"   ❌ {table[0]}: Error counting rows - {e}")
        
        conn.close()
        return integrity_ok and quick_ok
        
    except sqlite3.DatabaseError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function to test both databases"""
    print("🔍 WhatsApp Bridge Database Corruption Diagnostic Tool")
    print("=" * 60)
    
    whatsapp_bridge_dir = Path("whatsapp-bridge")
    store_dir = whatsapp_bridge_dir / "store"
    
    if not store_dir.exists():
        print(f"❌ Store directory not found: {store_dir}")
        sys.exit(1)
    
    # Test both databases
    whatsapp_db = store_dir / "whatsapp.db"
    messages_db = store_dir / "messages.db"
    
    whatsapp_ok = test_database_integrity(whatsapp_db)
    messages_ok = test_database_integrity(messages_db)
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY:")
    print(f"   WhatsApp session DB (whatsapp.db): {'✅ OK' if whatsapp_ok else '❌ CORRUPTED'}")
    print(f"   Messages DB (messages.db): {'✅ OK' if messages_ok else '❌ CORRUPTED'}")
    
    if not whatsapp_ok or not messages_ok:
        print("\n🚨 CORRUPTION DETECTED!")
        print("   One or more databases are corrupted and need to be repaired or recreated.")
        print("   Run the database recovery script to fix this issue.")
        return 1
    else:
        print("\n✅ All databases are healthy!")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 