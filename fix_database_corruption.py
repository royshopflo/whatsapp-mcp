#!/usr/bin/env python3
"""
WhatsApp Bridge Database Recovery Tool
This script attempts to recover corrupted SQLite databases for the WhatsApp bridge
"""

import sqlite3
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

def backup_database(db_path, backup_suffix="corrupted"):
    """Create a backup of the database before attempting recovery"""
    if not os.path.exists(db_path):
        print(f"❌ Database file does not exist: {db_path}")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.{backup_suffix}_{timestamp}"
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Created backup: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return None

def attempt_database_recovery(db_path):
    """Attempt to recover a corrupted SQLite database"""
    print(f"\n🔧 Attempting to recover database: {db_path}")
    
    # First, create a backup
    backup_path = backup_database(db_path)
    if not backup_path:
        return False
    
    recovery_path = f"{db_path}.recovered"
    
    try:
        # Method 1: Try .dump and restore
        print("📄 Attempting dump and restore method...")
        
        # Open the corrupted database
        source_conn = sqlite3.connect(db_path)
        
        # Create a new database
        dest_conn = sqlite3.connect(recovery_path)
        
        # Try to dump the schema and data
        for line in source_conn.iterdump():
            try:
                dest_conn.execute(line)
            except sqlite3.Error as e:
                print(f"⚠️  Skipping corrupted line: {e}")
                continue
        
        dest_conn.commit()
        source_conn.close()
        dest_conn.close()
        
        # Test the recovered database
        test_conn = sqlite3.connect(recovery_path)
        test_cursor = test_conn.cursor()
        
        # Run integrity check
        result = test_cursor.execute("PRAGMA integrity_check").fetchone()
        test_conn.close()
        
        if result[0] == "ok":
            # Replace the original with the recovered version
            shutil.move(recovery_path, db_path)
            print("✅ Database recovered successfully!")
            return True
        else:
            print(f"❌ Recovered database still has issues: {result[0]}")
            os.remove(recovery_path)
            return False
            
    except Exception as e:
        print(f"❌ Recovery failed: {e}")
        # Clean up recovery file if it exists
        if os.path.exists(recovery_path):
            os.remove(recovery_path)
        return False

def recreate_whatsapp_database(db_path):
    """Recreate the WhatsApp session database from scratch"""
    print(f"\n🔄 Recreating WhatsApp session database: {db_path}")
    
    # Backup the corrupted database
    backup_path = backup_database(db_path, "before_recreate")
    if not backup_path:
        return False
    
    try:
        # Remove the corrupted database
        os.remove(db_path)
        
        # Create a new empty database
        # The Go WhatsApp library will recreate the schema when it starts
        conn = sqlite3.connect(db_path)
        conn.close()
        
        print("✅ New WhatsApp session database created")
        print("⚠️  You will need to scan the QR code again to re-authenticate")
        return True
        
    except Exception as e:
        print(f"❌ Failed to recreate database: {e}")
        return False

def recreate_messages_database(db_path):
    """Recreate the messages database with proper schema"""
    print(f"\n🔄 Recreating messages database: {db_path}")
    
    # Backup the corrupted database
    backup_path = backup_database(db_path, "before_recreate")
    if not backup_path:
        return False
    
    try:
        # Remove the corrupted database
        os.remove(db_path)
        
        # Create a new database with the correct schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Recreate the schema from main.go
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                jid TEXT PRIMARY KEY,
                name TEXT,
                last_message_time TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT,
                chat_jid TEXT,
                sender TEXT,
                content TEXT,
                timestamp TIMESTAMP,
                is_from_me BOOLEAN,
                media_type TEXT,
                filename TEXT,
                url TEXT,
                media_key BLOB,
                file_sha256 BLOB,
                file_enc_sha256 BLOB,
                file_length INTEGER,
                PRIMARY KEY (id, chat_jid),
                FOREIGN KEY (chat_jid) REFERENCES chats(jid)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ New messages database created with proper schema")
        print("⚠️  Message history has been lost, but new messages will be stored")
        return True
        
    except Exception as e:
        print(f"❌ Failed to recreate messages database: {e}")
        return False

def test_database_integrity(db_path):
    """Test if a database is healthy"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        result = cursor.execute("PRAGMA integrity_check").fetchone()
        conn.close()
        return result[0] == "ok"
    except:
        return False

def main():
    """Main recovery function"""
    print("🔧 WhatsApp Bridge Database Recovery Tool")
    print("=" * 50)
    
    whatsapp_bridge_dir = Path("whatsapp-bridge")
    store_dir = whatsapp_bridge_dir / "store"
    
    if not store_dir.exists():
        print(f"❌ Store directory not found: {store_dir}")
        sys.exit(1)
    
    whatsapp_db = store_dir / "whatsapp.db"
    messages_db = store_dir / "messages.db"
    
    # Check current state
    whatsapp_ok = test_database_integrity(whatsapp_db)
    messages_ok = test_database_integrity(messages_db)
    
    print(f"📊 Current status:")
    print(f"   WhatsApp DB: {'✅ OK' if whatsapp_ok else '❌ CORRUPTED'}")
    print(f"   Messages DB: {'✅ OK' if messages_ok else '❌ CORRUPTED'}")
    
    if whatsapp_ok and messages_ok:
        print("\n✅ All databases are healthy! No recovery needed.")
        return 0
    
    print("\n🚨 Starting recovery process...")
    
    recovery_success = True
    
    # Recover WhatsApp database
    if not whatsapp_ok:
        print(f"\n🔧 Processing WhatsApp session database...")
        
        # First try recovery
        if not attempt_database_recovery(whatsapp_db):
            print("⚠️  Recovery failed, recreating database...")
            if not recreate_whatsapp_database(whatsapp_db):
                recovery_success = False
    
    # Recover Messages database
    if not messages_ok:
        print(f"\n🔧 Processing messages database...")
        
        # First try recovery
        if not attempt_database_recovery(messages_db):
            print("⚠️  Recovery failed, recreating database...")
            if not recreate_messages_database(messages_db):
                recovery_success = False
    
    # Final verification
    print("\n📋 Verifying recovery...")
    whatsapp_final = test_database_integrity(whatsapp_db)
    messages_final = test_database_integrity(messages_db)
    
    print(f"   WhatsApp DB: {'✅ OK' if whatsapp_final else '❌ STILL CORRUPTED'}")
    print(f"   Messages DB: {'✅ OK' if messages_final else '❌ STILL CORRUPTED'}")
    
    if whatsapp_final and messages_final:
        print("\n🎉 Database recovery completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Restart the WhatsApp bridge service")
        print("   2. If the WhatsApp session was recreated, scan the QR code to re-authenticate")
        print("   3. Monitor the logs for any remaining issues")
        return 0
    else:
        print("\n❌ Recovery failed. Manual intervention may be required.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 