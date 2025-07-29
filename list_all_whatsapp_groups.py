#!/usr/bin/env python3
"""
Script to list all WhatsApp groups from the database
Shows group names, JIDs, member counts, and last activity
"""

import sys
import os
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

def get_all_whatsapp_groups() -> List[Dict[str, Any]]:
    """Get all WhatsApp groups from the database"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'whatsapp-bridge', 'store', 'messages.db')
        
        if not os.path.exists(db_path):
            print(f"❌ Database not found at: {db_path}")
            return []
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all group chats (JIDs ending with @g.us)
        cursor.execute("""
            SELECT 
                jid,
                name,
                last_message_time
            FROM chats
            WHERE jid LIKE '%@g.us'
            ORDER BY name ASC
        """)
        
        groups = []
        for row in cursor.fetchall():
            jid, name, last_message_time = row
            
            # Get message count for this group
            cursor.execute("""
                SELECT COUNT(*) as message_count
                FROM messages
                WHERE chat_jid = ?
            """, (jid,))
            
            message_result = cursor.fetchone()
            message_count = message_result[0] if message_result else 0
            
            # Get recent message count (last 7 days)
            seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S%z')
            cursor.execute("""
                SELECT COUNT(*) as recent_count
                FROM messages
                WHERE chat_jid = ? AND timestamp >= ?
            """, (jid, seven_days_ago))
            
            recent_result = cursor.fetchone()
            recent_count = recent_result[0] if recent_result else 0
            
            groups.append({
                'jid': jid,
                'name': name or 'Unnamed Group',
                'last_message_time': last_message_time,
                'total_messages': message_count,
                'recent_messages_7d': recent_count
            })
        
        conn.close()
        return groups
        
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        return []

def categorize_group(group_name: str) -> str:
    """Categorize group based on name patterns"""
    name_lower = group_name.lower()
    
    # Internal groups
    internal_patterns = [
        'solutions war room', 'shopflo war room', 'priority inbox check',
        'shopflo customer success', 'shopflo - onboarding', 'shopflo sales',
        'shopflo team', 'internal', 'team', 'onboarding-internal'
    ]
    
    for pattern in internal_patterns:
        if pattern in name_lower:
            return '🏠 INTERNAL'
    
    # Partner integration groups
    partner_patterns = [
        'shopflo <>', 'shopflo x', '<> shopflo', 'x shopflo',
        'sirevest', 'indulgeo', 'cai store', 'nutrabox', 'urban jungle',
        'ageasy', 'koparo', 'goodbug', 'marvans', 'antinorm', 'qubo'
    ]
    
    for pattern in partner_patterns:
        if pattern in name_lower:
            return '🤝 PARTNER'
    
    # Customer groups (specific known customers)
    customer_patterns = [
        'emma', 'borngood', 'boult', 'traya', 'renee cosmetics',
        'naturup', 'tribal veda'
    ]
    
    for pattern in customer_patterns:
        if pattern in name_lower:
            return '🏢 CUSTOMER'
    
    # Support groups
    if '(sos)' in name_lower or 'support' in name_lower:
        return '🆘 SUPPORT'
    
    # Community groups
    community_patterns = ['jiu-jitsu', 'performers club', 'flamingo']
    for pattern in community_patterns:
        if pattern in name_lower:
            return '👥 COMMUNITY'
    
    # Revenue/business groups
    if 'revenue' in name_lower or 'business' in name_lower:
        return '💰 BUSINESS'
    
    # Default
    return '❓ OTHER'

def format_last_activity(last_message_time: str) -> str:
    """Format last activity time in a readable way"""
    if not last_message_time:
        return "No activity"
    
    try:
        # Parse the timestamp
        if '+' in last_message_time:
            dt = datetime.fromisoformat(last_message_time)
        else:
            dt = datetime.fromisoformat(last_message_time + '+00:00')
        
        now = datetime.now(timezone.utc)
        diff = now - dt
        
        if diff.days > 30:
            return f"{diff.days} days ago"
        elif diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "Just now"
    except:
        return last_message_time[:10] if len(last_message_time) > 10 else last_message_time

def main():
    """Main function to list all WhatsApp groups"""
    print("📱 WhatsApp Groups List")
    print("=" * 80)
    
    groups = get_all_whatsapp_groups()
    
    if not groups:
        print("❌ No groups found or unable to access database")
        return
    
    print(f"📊 Total Groups Found: {len(groups)}")
    print("=" * 80)
    
    # Categorize groups
    categories = {}
    for group in groups:
        category = categorize_group(group['name'])
        if category not in categories:
            categories[category] = []
        categories[category].append(group)
    
    # Display by category
    category_order = ['🏢 CUSTOMER', '🤝 PARTNER', '🏠 INTERNAL', '🆘 SUPPORT', 
                     '👥 COMMUNITY', '💰 BUSINESS', '❓ OTHER']
    
    for category in category_order:
        if category in categories:
            print(f"\n{category} ({len(categories[category])} groups)")
            print("-" * 60)
            
            # Sort by recent activity
            category_groups = sorted(categories[category], 
                                   key=lambda x: x['recent_messages_7d'], 
                                   reverse=True)
            
            for i, group in enumerate(category_groups, 1):
                name = group['name']
                jid = group['jid']
                total_msgs = group['total_messages']
                recent_msgs = group['recent_messages_7d']
                last_activity = format_last_activity(group['last_message_time'])
                
                # Truncate long names
                if len(name) > 40:
                    display_name = name[:37] + "..."
                else:
                    display_name = name
                
                print(f"{i:2d}. {display_name:<40} | Recent: {recent_msgs:3d} | Total: {total_msgs:4d} | Last: {last_activity}")
                print(f"    JID: {jid}")
                print()
    
    # Summary statistics
    print("=" * 80)
    print("📈 SUMMARY STATISTICS")
    print("=" * 80)
    
    total_messages = sum(group['total_messages'] for group in groups)
    total_recent = sum(group['recent_messages_7d'] for group in groups)
    active_groups = len([g for g in groups if g['recent_messages_7d'] > 0])
    
    print(f"📊 Total Groups: {len(groups)}")
    print(f"📈 Active Groups (7 days): {active_groups}")
    print(f"💬 Total Messages: {total_messages:,}")
    print(f"📱 Recent Messages (7 days): {total_recent:,}")
    
    print(f"\n📋 Category Breakdown:")
    for category, group_list in categories.items():
        recent_activity = sum(g['recent_messages_7d'] for g in group_list)
        print(f"  {category}: {len(group_list)} groups, {recent_activity} recent messages")
    
    print("\n✅ Complete groups list generated!")

if __name__ == "__main__":
    main() 