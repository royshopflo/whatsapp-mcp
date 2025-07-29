#!/usr/bin/env python3
"""
WhatsApp Groups Summary - Key Groups by Category and Activity
Provides a focused view of the most important groups
"""

import sys
import os
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

def get_key_groups_summary() -> None:
    """Generate a focused summary of key WhatsApp groups"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'whatsapp-bridge', 'store', 'messages.db')
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all group chats with activity data
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
                'recent_messages_7d': recent_count
            })
        
        conn.close()
        
        # Categorize and filter key groups
        print("📱 **WHATSAPP GROUPS SUMMARY - KEY GROUPS BY CATEGORY**")
        print("=" * 80)
        print(f"📊 Total Groups: {len(groups)} | Active (7 days): {len([g for g in groups if g['recent_messages_7d'] > 0])}")
        print("=" * 80)
        
        # 🏢 CUSTOMER GROUPS (Active)
        customer_groups = [g for g in groups if any(keyword in g['name'].lower() for keyword in 
                          ['emma', 'borngood', 'boult', 'traya', 'renee cosmetics', 'naturup', 'tribal veda'])]
        active_customers = [g for g in customer_groups if g['recent_messages_7d'] > 0]
        
        print(f"\n🏢 **CUSTOMER GROUPS** ({len(customer_groups)} total, {len(active_customers)} active)")
        print("-" * 60)
        customer_groups.sort(key=lambda x: x['recent_messages_7d'], reverse=True)
        for i, group in enumerate(customer_groups[:10], 1):
            status = "🟢 ACTIVE" if group['recent_messages_7d'] > 0 else "⚪ QUIET"
            print(f"{i:2d}. {group['name']:<40} | {status} ({group['recent_messages_7d']} msgs)")
        
        # 🏠 INTERNAL GROUPS (All)
        internal_groups = [g for g in groups if any(pattern in g['name'].lower() for pattern in 
                          ['solutions war room', 'shopflo war room', 'priority inbox check', 'shopflo customer success', 
                           'shopflo - onboarding', 'shopflo sales', 'support - internal', 'shopflo onboarding-internal',
                           'shopflo ops internal', 'core team', 'shopflo product', 'team table', 'a - team'])]
        
        print(f"\n🏠 **INTERNAL GROUPS** ({len(internal_groups)} groups)")
        print("-" * 60)
        internal_groups.sort(key=lambda x: x['recent_messages_7d'], reverse=True)
        for i, group in enumerate(internal_groups, 1):
            status = "🔥 VERY ACTIVE" if group['recent_messages_7d'] > 50 else "🟢 ACTIVE" if group['recent_messages_7d'] > 0 else "⚪ QUIET"
            print(f"{i:2d}. {group['name']:<40} | {status} ({group['recent_messages_7d']} msgs)")
        
        # 🤝 TOP PARTNER GROUPS (Most Active)
        partner_groups = [g for g in groups if any(pattern in g['name'].lower() for pattern in 
                         ['shopflo <>', 'shopflo x', '<> shopflo', 'x shopflo']) and 
                         not any(exc in g['name'].lower() for exc in ['(ob)', '(sos)', 'emma', 'borngood', 'boult', 'traya'])]
        active_partners = [g for g in partner_groups if g['recent_messages_7d'] > 0]
        
        print(f"\n🤝 **TOP ACTIVE PARTNER GROUPS** ({len(active_partners)} of {len(partner_groups)} active)")
        print("-" * 60)
        active_partners.sort(key=lambda x: x['recent_messages_7d'], reverse=True)
        for i, group in enumerate(active_partners[:15], 1):
            print(f"{i:2d}. {group['name']:<40} | 🟢 ACTIVE ({group['recent_messages_7d']} msgs)")
        
        # 👥 COMMUNITY GROUPS
        community_groups = [g for g in groups if any(pattern in g['name'].lower() for pattern in 
                           ['jiu-jitsu', 'performers club', 'flamingo'])]
        
        print(f"\n👥 **COMMUNITY GROUPS** ({len(community_groups)} groups)")
        print("-" * 60)
        community_groups.sort(key=lambda x: x['recent_messages_7d'], reverse=True)
        for i, group in enumerate(community_groups, 1):
            status = "🟢 ACTIVE" if group['recent_messages_7d'] > 0 else "⚪ QUIET"
            print(f"{i:2d}. {group['name']:<40} | {status} ({group['recent_messages_7d']} msgs)")
        
        # 📈 TOP ACTIVE GROUPS (All Categories)
        print(f"\n📈 **MOST ACTIVE GROUPS (ALL CATEGORIES)**")
        print("-" * 60)
        all_active = [g for g in groups if g['recent_messages_7d'] > 20]
        all_active.sort(key=lambda x: x['recent_messages_7d'], reverse=True)
        for i, group in enumerate(all_active[:20], 1):
            category = "🏠 INTERNAL" if any(p in group['name'].lower() for p in ['war room', 'internal', 'team', 'support']) else \
                      "🏢 CUSTOMER" if any(p in group['name'].lower() for p in ['emma', 'borngood', 'boult']) else \
                      "🤝 PARTNER" if any(p in group['name'].lower() for p in ['shopflo', '<>', 'x ']) else \
                      "❓ OTHER"
            print(f"{i:2d}. {group['name'][:45]:<45} | {category} ({group['recent_messages_7d']} msgs)")
        
        # 💤 INACTIVE GROUPS (High message count but no recent activity)
        print(f"\n💤 **POTENTIALLY DORMANT GROUPS** (Many messages but no recent activity)")
        print("-" * 60)
        
        # Get total message counts for inactive groups
        inactive_high_volume = []
        for group in groups:
            if group['recent_messages_7d'] == 0:
                cursor = sqlite3.connect(db_path).cursor()
                cursor.execute("SELECT COUNT(*) FROM messages WHERE chat_jid = ?", (group['jid'],))
                result = cursor.fetchone()
                total_messages = result[0] if result else 0
                if total_messages > 100:
                    group['total_messages'] = total_messages
                    inactive_high_volume.append(group)
        
        inactive_high_volume.sort(key=lambda x: x['total_messages'], reverse=True)
        for i, group in enumerate(inactive_high_volume[:10], 1):
            print(f"{i:2d}. {group['name'][:45]:<45} | 💤 DORMANT ({group['total_messages']} total msgs)")
        
        print("\n" + "=" * 80)
        print("📊 **SUMMARY INSIGHTS:**")
        
        total_recent_messages = sum(g['recent_messages_7d'] for g in groups)
        customer_activity = sum(g['recent_messages_7d'] for g in customer_groups)
        internal_activity = sum(g['recent_messages_7d'] for g in internal_groups)
        
        print(f"• 📱 Total Recent Activity: {total_recent_messages:,} messages (7 days)")
        print(f"• 🏢 Customer Activity: {customer_activity} messages ({customer_activity/total_recent_messages*100:.1f}%)")
        print(f"• 🏠 Internal Activity: {internal_activity} messages ({internal_activity/total_recent_messages*100:.1f}%)")
        print(f"• 🤝 Partner Activity: {sum(g['recent_messages_7d'] for g in active_partners)} messages")
        print(f"• 📈 Most Active Category: {'Internal' if internal_activity > customer_activity else 'Customer'} Communication")
        
        print("\n✅ WhatsApp Groups Summary Complete!")
        
    except Exception as e:
        print(f"❌ Error generating summary: {e}")

if __name__ == "__main__":
    get_key_groups_summary() 