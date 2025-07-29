#!/usr/bin/env python3
"""
Dynamic WhatsApp Groups Analysis - Real-time analysis of actual groups
Analyzes each group individually with current activity and sentiment
"""

import sys
import os
import sqlite3
import re
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple

# Add the whatsapp-mcp-server to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'whatsapp-mcp-server'))

try:
    import whatsapp
except ImportError as e:
    print(f"❌ Error importing WhatsApp module: {e}")
    print("Make sure you're running this from the correct directory")
    sys.exit(1)

# Target group
TARGET_GROUP_NAME = "Priority inbox check"
TARGET_GROUP_JID = "120363419811982156@g.us"

class DynamicGroupAnalyzer:
    def __init__(self):
        # Use IST timezone to match database timestamps (+05:30)
        ist_offset = timezone(timedelta(hours=5, minutes=30))
        self.analysis_date = datetime.now(ist_offset)
        
        # Database path
        self.db_path = os.path.join(os.path.dirname(__file__), 'whatsapp-bridge', 'store', 'messages.db')
        
        # Keywords for sentiment analysis
        self.negative_keywords = [
            'problem', 'issue', 'error', 'bug', 'fail', 'broken', 'not working',
            'crash', 'down', 'slow', 'timeout', 'refund', 'cancel', 'stuck',
            'help', 'urgent', 'critical', 'emergency', 'won\'t work', 'can\'t',
            'unable', 'frustrated', 'angry', 'disappointed', 'terrible', 'awful'
        ]
        
        self.positive_keywords = [
            'great', 'awesome', 'perfect', 'excellent', 'amazing', 'love',
            'fantastic', 'wonderful', 'good', 'nice', 'thanks', 'thank you',
            'solved', 'fixed', 'working', 'success', 'completed', 'done'
        ]
        
        self.urgent_keywords = [
            'urgent', 'emergency', 'asap', 'immediately', 'critical', 'priority',
            'escalate', 'escalation', 'issue', 'problem', 'help needed'
        ]

    def categorize_group(self, group_name: str, jid: str) -> Tuple[str, str]:
        """Categorize group as Customer, Partner, or Internal"""
        name_lower = group_name.lower()
        
        # Internal groups - only genuine internal keywords
        internal_keywords = [
            'internal', 'support', 'war room', 'solution', 'team', 
            'phonepe'
        ]
        if any(keyword in name_lower for keyword in internal_keywords):
            return 'Internal', '🏠'
        
        # Partner/Onboarding groups (start with OB)
        if name_lower.startswith('(ob)') or 'onboarding' in name_lower:
            return 'Partner', '🤝'
        
        # Customer groups (contain company names but not OB or internal keywords)
        if 'shopflo' in name_lower and not name_lower.startswith('(ob)'):
            return 'Customer', '🏢'
        
        # Default to Partner for other integrations
        return 'Partner', '🤝'

    def analyze_sentiment(self, messages: List[str]) -> Tuple[str, int]:
        """Analyze sentiment of recent messages"""
        if not messages:
            return 'neutral', 0
        
        negative_score = 0
        positive_score = 0
        urgent_score = 0
        
        for message in messages:
            message_lower = message.lower()
            
            # Count negative keywords
            negative_score += sum(1 for keyword in self.negative_keywords if keyword in message_lower)
            
            # Count positive keywords  
            positive_score += sum(1 for keyword in self.positive_keywords if keyword in message_lower)
            
            # Count urgent keywords
            urgent_score += sum(1 for keyword in self.urgent_keywords if keyword in message_lower)
        
        # Determine overall sentiment
        if urgent_score > 0:
            return 'urgent', urgent_score
        elif negative_score > positive_score:
            return 'negative', negative_score
        elif positive_score > negative_score:
            return 'positive', positive_score
        else:
            return 'neutral', 0

    def get_group_activity_analysis(self) -> Dict[str, Any]:
        """Get comprehensive analysis of all groups"""
        
        if not os.path.exists(self.db_path):
            return {"error": "Database not found"}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all groups with recent activity (last 24 hours) - excluding internal and OB groups
        cursor.execute("""
            SELECT 
                c.jid, 
                c.name, 
                c.last_message_time,
                COUNT(m.id) as message_count_24h
            FROM chats c 
            LEFT JOIN messages m ON c.jid = m.chat_jid 
                AND m.timestamp > datetime('now', '-24 hours')
            WHERE c.jid LIKE '%@g.us'
            AND c.name NOT LIKE '%internal%'
            AND c.name NOT LIKE '%support%' 
            AND c.name NOT LIKE '%war room%'
            AND c.name NOT LIKE '%solution%'
            AND c.name NOT LIKE '%team%'
            AND c.name NOT LIKE '(OB)%'
            AND c.name NOT LIKE '%onboarding%'
            AND c.name NOT LIKE '%phonepe%'
            AND c.name NOT LIKE '%Phonepe%'
            AND c.name NOT LIKE '%PhonePe%'
            GROUP BY c.jid, c.name, c.last_message_time
            ORDER BY message_count_24h DESC, c.last_message_time DESC
        """)
        
        groups_data = cursor.fetchall()
        
        # Get recent messages for sentiment analysis
        group_messages = {}
        for jid, name, last_time, count in groups_data:
            if count > 0:  # Only get messages for active groups
                cursor.execute("""
                    SELECT content 
                    FROM messages 
                    WHERE chat_jid = ? 
                    AND timestamp > datetime('now', '-24 hours')
                    AND content IS NOT NULL 
                    AND content != ''
                    ORDER BY timestamp DESC 
                    LIMIT 10
                """, (jid,))
                
                messages = [row[0] for row in cursor.fetchall() if row[0]]
                group_messages[jid] = messages
        
        conn.close()
        
        # Analyze each group (excluding internal and OB groups)
        analysis = {
            'total_groups': 0,  # Will count customer groups only
            'active_groups_24h': 0,  # Will count customer active groups only
            'categories': {'Customer': []},  # Only customer groups
            'critical_groups': [],
            'top_active': [],
            'sentiment_summary': {'positive': 0, 'negative': 0, 'urgent': 0, 'neutral': 0}
        }
        
        for jid, name, last_time, message_count in groups_data:
            category, emoji = self.categorize_group(name, jid)
            
            # Skip internal and partner/OB groups completely
            if category == 'Internal' or category == 'Partner':
                continue
                
            # Analyze sentiment for active groups
            sentiment = 'neutral'
            sentiment_score = 0
            if jid in group_messages:
                sentiment, sentiment_score = self.analyze_sentiment(group_messages[jid])
            
            group_info = {
                'jid': jid,
                'name': name,
                'last_activity': last_time,
                'message_count_24h': message_count,
                'sentiment': sentiment,
                'sentiment_score': sentiment_score,
                'emoji': emoji
            }
            
            # Categorize
            analysis['categories'][category].append(group_info)
            
            # Track sentiment
            analysis['sentiment_summary'][sentiment] += 1
            
            # Identify critical groups (urgent sentiment or high negative sentiment)
            if sentiment == 'urgent' or (sentiment == 'negative' and sentiment_score >= 3):
                analysis['critical_groups'].append(group_info)
            
            # Track top active groups
            if message_count > 0:
                analysis['top_active'].append(group_info)
        
        # Update final counts (customer groups only)
        analysis['total_groups'] = len(analysis['categories']['Customer'])
        analysis['active_groups_24h'] = len([g for g in analysis['categories']['Customer'] if g['message_count_24h'] > 0])
        
        # Keep only top 10 most active
        analysis['top_active'] = analysis['top_active'][:10]
        
        # Sort critical groups by severity
        analysis['critical_groups'].sort(key=lambda x: x['sentiment_score'], reverse=True)
        
        return analysis

    def generate_analysis_message(self, analysis: Dict[str, Any]) -> str:
        """Generate formatted analysis message"""
        
        if 'error' in analysis:
            return f"❌ {analysis['error']}"
        
        # Summary statistics
        total_groups = analysis['total_groups']
        active_groups = analysis['active_groups_24h']
        customer_count = len(analysis['categories']['Customer'])
        
        # Critical alerts
        critical_count = len(analysis['critical_groups'])
        urgent_count = analysis['sentiment_summary']['urgent']
        negative_count = analysis['sentiment_summary']['negative']
        
        message = f"""📊 **CUSTOMER GROUPS ANALYSIS**
📋 *Customer Groups Only (Internal & OB Groups Excluded)*

🎯 **Real-time Summary** ({self.analysis_date.strftime('%Y-%m-%d %H:%M:%S IST')})
• 📊 Total Customer Groups: {total_groups}
• 📈 Active Customers (24h): {active_groups}
• 🏢 Direct Customer Integrations: {customer_count}

🚨 **ALERTS & STATUS:**
• 🚨 **CRITICAL**: {critical_count} groups
• ⚠️ **URGENT**: {urgent_count} groups
• 🔴 **NEGATIVE**: {negative_count} groups
• ✅ **STABLE**: {active_groups - critical_count} groups"""

        # Critical groups details
        if analysis['critical_groups']:
            message += "\n\n🚨 **CRITICAL GROUPS REQUIRING ATTENTION:**"
            for i, group in enumerate(analysis['critical_groups'][:5], 1):
                sentiment_emoji = '🚨' if group['sentiment'] == 'urgent' else '🔴'
                message += f"\n{i}. {sentiment_emoji} **{group['name']}**"
                message += f"\n   • Messages: {group['message_count_24h']} (24h)"
                message += f"\n   • Sentiment: {group['sentiment'].upper()} (score: {group['sentiment_score']})"
                if group['last_activity']:
                    message += f"\n   • Last activity: {group['last_activity']}"
                message += "\n"

        # Top active groups
        if analysis['top_active']:
            message += "\n📈 **TOP ACTIVE CUSTOMER GROUPS (24h):**"
            for i, group in enumerate(analysis['top_active'][:8], 1):
                category_emoji = group['emoji']
                sentiment_emoji = {'urgent': '🚨', 'negative': '🔴', 'positive': '✅', 'neutral': '⚪'}[group['sentiment']]
                message += f"\n{i}. {category_emoji}{sentiment_emoji} **{group['name']}** ({group['message_count_24h']} msgs)"

        # Customer groups summary
        customer_groups = analysis['categories']['Customer']
        if customer_groups:
            active_customers = [g for g in customer_groups if g['message_count_24h'] > 0]
            quiet_customers = [g for g in customer_groups if g['message_count_24h'] == 0]
            
            message += f"\n\n🏢 **CUSTOMER STATUS BREAKDOWN:**"
            message += f"\n• 📈 **Active Today**: {len(active_customers)} customers"
            message += f"\n• 😴 **Quiet Today**: {len(quiet_customers)} customers"
            
            if active_customers:
                message += "\n\n📊 **Most Active Customers:**"
                for i, group in enumerate(active_customers[:5], 1):
                    sentiment_emoji = {'urgent': '🚨', 'negative': '🔴', 'positive': '✅', 'neutral': '⚪'}[group['sentiment']]
                    message += f"\n{i}. {sentiment_emoji} **{group['name']}** ({group['message_count_24h']} msgs)"

        message += f"\n\n📊 **Generated by Customer-Focused WhatsApp Monitor**"
        message += f"\n🔄 Next update in 1 hour | Focus: Direct Customers Only"
        
        return message

def send_dynamic_analysis():
    """Send dynamic analysis to Priority inbox check group"""
    
    print("📊 Dynamic WhatsApp Groups Analysis")
    print("=" * 50)
    
    analyzer = DynamicGroupAnalyzer()
    
    print("🔍 Analyzing real-time group data...")
    analysis = analyzer.get_group_activity_analysis()
    
    print("📝 Generating dynamic analysis message...")
    message = analyzer.generate_analysis_message(analysis)
    
    print("Analysis preview:")
    print("-" * 40)
    print(message)
    print("-" * 40)
    
    # Send the message
    try:
        print(f"\n🚀 Sending to {TARGET_GROUP_NAME}...")
        result = whatsapp.send_message(TARGET_GROUP_JID, message)
        
        if result:
            print("✅ Dynamic analysis successfully sent!")
            return True
        else:
            print("❌ Failed to send message")
            return False
            
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

def main():
    """Main function"""
    success = send_dynamic_analysis()
    
    if success:
        print("\n🎉 SUCCESS!")
        print("📱 Real-time analysis delivered to Priority inbox check group")
    else:
        print("\n💔 FAILED!")
        print("🔧 Please check WhatsApp bridge connection and try again")

if __name__ == "__main__":
    main() 