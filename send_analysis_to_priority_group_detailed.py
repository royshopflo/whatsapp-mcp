#!/usr/bin/env python3
"""
Script to send detailed WhatsApp groups analysis to Priority inbox check group
Provides individual analysis for each group, not just summary
"""

import sys
import os
import sqlite3
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

class DetailedGroupAnalyzer:
    def __init__(self):
        # Use IST timezone to match database timestamps (+05:30)
        ist_offset = timezone(timedelta(hours=5, minutes=30))
        self.analysis_date = datetime.now(ist_offset)
        
        # Look back 24 hours for comprehensive analysis
        self.lookback_hours = 24
        self.since_date = self.analysis_date - timedelta(hours=self.lookback_hours)
        
        # Enhanced sentiment keywords including context clues
        self.negative_keywords = [
            'problem', 'issue', 'error', 'bug', 'fail', 'broken', 'not working',
            'crash', 'down', 'slow', 'timeout', 'refund', 'cancel', 'stop',
            'quit', 'leave', 'frustrated', 'angry', 'disappointed', 'confused',
            'stuck', 'help', 'urgent', 'critical', 'emergency', 'won\'t work',
            'doesn\'t work', 'can\'t', 'unable', 'impossible', 'terrible',
            'awful', 'worst', 'hate', 'horrible', 'useless', 'waste'
        ]
        
        # Context clue keywords that indicate ongoing issues
        self.issue_context_keywords = [
            'checking', 'looking into', 'will fix', 'fixing', 'any update',
            'update??', 'still waiting', 'when will', 'how long', 'ETA',
            'not resolved', 'still not', 'pending', 'follow up', 'status',
            'investigating', 'working on', 'team is checking'
        ]
        
        self.positive_keywords = [
            'good', 'great', 'excellent', 'perfect', 'awesome', 'amazing',
            'love', 'like', 'happy', 'satisfied', 'working', 'success',
            'solved', 'fixed', 'resolved', 'thank', 'thanks', 'appreciate',
            'helpful', 'useful', 'easy', 'simple', 'smooth', 'fast',
            'quick', 'efficient', 'brilliant', 'wonderful', 'fantastic'
        ]
        
        # Internal team identifiers
        self.internal_team = set()
        
        # Define all important groups to analyze
        self.important_groups = [
            # Customer/Merchant Groups
            'Shopflo <> Emma',
            'BornGood || Shopflow',
            'Boult / Shopflo', 
            'Traya || Easebuzz',
            'Renee Cosmetics<>Appmaker',
            'NaturUp<>shopflo',
            'Shopflo<> Tribal Veda',
            'Shopflo <> Traya.health',
            
            # Top Active Partner Groups (from our previous analysis)
            'Shopflo <> Indulgeo Essentials',
            'Sirevest x Shopflo',
            'Shopflo <> The Cai Store',
            'Shopflo x Nutrabox',
            'Shopflo <> Urban Jungle',
            'Shopflo <> AgeasyByAntara',
            'Shopflo x Koparo',
            'Shopflo <> TheGoodBug',
            'Shopflo x Marvans Accessories',
            'Shopflo <> Antinorm',
            'Shopflo x Qubo',
            
            # Support Groups
            'Solutions War Room',
            'Priority inbox check',
            
            # Internal Groups  
            'Shopflo customer success',
            'Shopflo - onboarding',
            'Shopflo Sales<>CS'
        ]

    def identify_internal_team_direct(self) -> None:
        """Identify internal team members from internal groups using direct DB access"""
        try:
            db_path = os.path.join(os.path.dirname(__file__), 'whatsapp-bridge', 'store', 'messages.db')
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get internal groups
            internal_patterns = ['%shopflo team%', '%internal%', '%team%', '%onboarding-internal%']
            
            for pattern in internal_patterns:
                cursor.execute("""
                    SELECT DISTINCT messages.sender
                    FROM messages
                    JOIN chats ON messages.chat_jid = chats.jid
                    WHERE LOWER(chats.name) LIKE LOWER(?) 
                    AND messages.is_from_me = 0
                    AND chats.jid LIKE '%@g.us'
                    LIMIT 50
                """, (pattern,))
                
                for row in cursor.fetchall():
                    if row[0]:  # sender is not null
                        self.internal_team.add(row[0])
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error identifying internal team: {e}")

    def get_group_data(self, group_name: str) -> Dict[str, Any]:
        """Get data for a specific group"""
        try:
            db_path = os.path.join(os.path.dirname(__file__), 'whatsapp-bridge', 'store', 'messages.db')
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get group data
            cursor.execute("""
                SELECT jid, name, last_message_time
                FROM chats
                WHERE name = ? AND jid LIKE '%@g.us'
            """, (group_name,))
            
            group_row = cursor.fetchone()
            if not group_row:
                conn.close()
                return None
                
            jid, name, last_message_time = group_row
            
            # Get recent messages for this group
            cursor.execute("""
                SELECT timestamp, sender, content, is_from_me, id
                FROM messages
                WHERE chat_jid = ? AND timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT 20
            """, (jid, self.since_date.strftime('%Y-%m-%d %H:%M:%S%z')))
            
            messages = []
            for msg_row in cursor.fetchall():
                messages.append({
                    'timestamp': msg_row[0],
                    'sender': msg_row[1],
                    'content': msg_row[2] or '',
                    'is_from_me': msg_row[3],
                    'id': msg_row[4]
                })
            
            conn.close()
            
            return {
                'name': name,
                'jid': jid,
                'last_message_time': last_message_time,
                'recent_message_count': len(messages),
                'recent_messages': messages
            }
            
        except Exception as e:
            print(f"❌ Error getting group data for {group_name}: {e}")
            return None

    def analyze_sentiment(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhanced sentiment analysis including context clues"""
        if not messages:
            return {'sentiment_score': 0, 'total_messages': 0, 'negative_ratio': 0, 'issues': [], 'status': 'NO_ACTIVITY'}
        
        total_messages = 0
        sentiment_score = 0
        negative_count = 0
        issues = []
        
        for msg in messages:
            content = msg.get('content', '').lower()
            sender = msg.get('sender', '')
            
            # Skip internal team messages for sentiment analysis
            if sender in self.internal_team:
                continue
                
            total_messages += 1
            message_sentiment = 0
            
            # Check for negative sentiment keywords
            for keyword in self.negative_keywords:
                if keyword in content:
                    message_sentiment -= 1
                    negative_count += 1
                    issues.append(content[:100] + "..." if len(content) > 100 else content)
                    break
            
            # Check for issue context clues (indicates ongoing problems)
            if message_sentiment == 0:  # Only if not already negative
                for keyword in self.issue_context_keywords:
                    if keyword in content:
                        message_sentiment -= 0.5  # Lighter negative weight for context clues
                        negative_count += 0.5
                        issues.append(f"Context: {content[:80]}..." if len(content) > 80 else f"Context: {content}")
                        break
            
            # Check for positive sentiment
            if message_sentiment == 0:  # Only if not already negative
                for keyword in self.positive_keywords:
                    if keyword in content:
                        message_sentiment += 1
                        break
            
            sentiment_score += message_sentiment
        
        if total_messages == 0:
            return {'sentiment_score': 0, 'total_messages': 0, 'negative_ratio': 0, 'issues': [], 'status': 'NO_CUSTOMER_ACTIVITY'}
        
        negative_ratio = (negative_count / total_messages * 100) if total_messages > 0 else 0
        
        # Determine status
        if negative_ratio >= 20:
            status = 'CRITICAL'
        elif negative_ratio >= 10:
            status = 'AT_RISK' 
        elif negative_ratio >= 5:
            status = 'MINOR_ISSUES'
        else:
            status = 'STABLE'
        
        return {
            'sentiment_score': sentiment_score,
            'total_messages': total_messages,
            'negative_ratio': negative_ratio,
            'issues': issues[:2],  # Top 2 issues
            'status': status
        }

    def generate_detailed_analysis(self) -> str:
        """Generate detailed analysis for all important groups"""
        print("🔄 Analyzing all important groups individually...")
        self.identify_internal_team_direct()
        group_analyses = []
        # Use dynamic group selection
        for group in get_refined_external_groups():
            group_data = self.get_group_data(group['name'])
            if group_data:
                sentiment_data = self.analyze_sentiment(group_data['recent_messages'])
                group_analyses.append({
                    'name': group['name'],
                    'data': group_data,
                    'sentiment': sentiment_data
                })
        if not group_analyses:
            return "❌ No group data found for analysis"
        
        # Sort by priority: Critical first, then by activity
        def sort_priority(group):
            status_priority = {
                'CRITICAL': 0, 'AT_RISK': 1, 'MINOR_ISSUES': 2, 
                'STABLE': 3, 'NO_CUSTOMER_ACTIVITY': 4, 'NO_ACTIVITY': 5
            }
            return (status_priority.get(group['sentiment']['status'], 6), -group['data']['recent_message_count'])
        
        group_analyses.sort(key=sort_priority)
        
        # Generate report
        analysis_message = f"""📊 **DETAILED GROUPS ANALYSIS - LAST {self.lookback_hours}H**

🎯 **Executive Summary:**
• 📊 Groups Analyzed: {len(group_analyses)}
• 🕐 Period: {self.since_date.strftime('%H:%M')} to {self.analysis_date.strftime('%H:%M')} IST
• 🏢 Internal Team: {len(self.internal_team)} members identified

"""

        # Count by status
        status_counts = {'CRITICAL': 0, 'AT_RISK': 0, 'MINOR_ISSUES': 0, 'STABLE': 0, 'NO_CUSTOMER_ACTIVITY': 0, 'NO_ACTIVITY': 0}
        for group in group_analyses:
            status_counts[group['sentiment']['status']] += 1

        analysis_message += f"""📈 **Status Breakdown:**
🚨 **CRITICAL: {status_counts['CRITICAL']}** | ⚠️ **AT RISK: {status_counts['AT_RISK']}** | 🔶 **MINOR: {status_counts['MINOR_ISSUES']}** 
✅ **STABLE: {status_counts['STABLE']}** | 😴 **QUIET: {status_counts['NO_CUSTOMER_ACTIVITY']}** | 💤 **INACTIVE: {status_counts['NO_ACTIVITY']}**

"""

        # Individual group details
        analysis_message += "📋 **INDIVIDUAL GROUP ANALYSIS:**\n\n"
        
        for group in group_analyses:
            name = group['name']
            sentiment = group['sentiment']
            data = group['data']
            
            # Status emoji
            status_emoji = {
                'CRITICAL': '🚨', 'AT_RISK': '⚠️', 'MINOR_ISSUES': '🔶',
                'STABLE': '✅', 'NO_CUSTOMER_ACTIVITY': '😴', 'NO_ACTIVITY': '💤'
            }
            
            emoji = status_emoji.get(sentiment['status'], '❓')
            
            analysis_message += f"**{emoji} {name}**\n"
            analysis_message += f"└ Status: {sentiment['status']}"
            
            if sentiment['total_messages'] > 0:
                analysis_message += f" | Messages: {sentiment['total_messages']} | Sentiment: {sentiment['negative_ratio']:.1f}% negative\n"
                if sentiment['issues']:
                    issue_text = sentiment['issues'][0][:60] + "..." if len(sentiment['issues'][0]) > 60 else sentiment['issues'][0]
                    analysis_message += f"└ Issue: \"{issue_text}\"\n"
            else:
                analysis_message += f" | No customer activity\n"
            
            analysis_message += "\n"
        
        # Action items
        critical_groups = [g for g in group_analyses if g['sentiment']['status'] == 'CRITICAL']
        at_risk_groups = [g for g in group_analyses if g['sentiment']['status'] == 'AT_RISK']
        
        analysis_message += "🎯 **ACTION ITEMS:**\n\n"
        
        if critical_groups:
            analysis_message += "**🚨 IMMEDIATE (Next 2 Hours):**\n"
            for group in critical_groups:
                analysis_message += f"• Contact {group['name']} - {group['sentiment']['negative_ratio']:.0f}% negative sentiment\n"
            analysis_message += "\n"
        
        if at_risk_groups:
            analysis_message += "**⚠️ SHORT TERM (Next 8 Hours):**\n"
            for group in at_risk_groups:
                analysis_message += f"• Monitor {group['name']} for escalation\n"
            analysis_message += "\n"
        
        if not critical_groups and not at_risk_groups:
            analysis_message += "• ✅ No immediate actions required\n"
            analysis_message += "• 🔄 Continue regular monitoring\n\n"
        
        analysis_message += f"Generated: {self.analysis_date.strftime('%Y-%m-%d %H:%M:%S IST')}\n"
        analysis_message += "Detailed Analysis by WhatsApp Groups Monitor"
        
        return analysis_message

def send_detailed_analysis_to_priority_group():
    """Send the detailed analysis to Priority inbox check group"""
    
    print("📱 Sending Detailed Analysis to Priority Inbox Check Group")
    print("=" * 70)
    print(f"Target Group: {TARGET_GROUP_NAME}")
    print(f"Group JID: {TARGET_GROUP_JID}")
    print("=" * 70)
    
    # Generate detailed analysis
    analyzer = DetailedGroupAnalyzer()
    analysis_message = analyzer.generate_detailed_analysis()
    
    print("📝 Detailed analysis message generated:")
    print("-" * 50)
    print(analysis_message[:500] + "..." if len(analysis_message) > 500 else analysis_message)
    print("-" * 50)
    
    # Verify group exists
    try:
        chat = whatsapp.get_chat(TARGET_GROUP_JID)
        if chat:
            print(f"✅ Group found: {chat.name}")
        else:
            print(f"❌ Group with JID {TARGET_GROUP_JID} not found")
            return False
    except Exception as e:
        print(f"❌ Error checking group: {e}")
        return False
    
    # Send the message
    try:
        print("\n🚀 Sending detailed analysis...")
        result = whatsapp.send_message(TARGET_GROUP_JID, analysis_message)
        
        if result:
            print("✅ Detailed analysis successfully sent to Priority inbox check group!")
            print("📋 Team now has individual group breakdown with specific action items")
            return True
        else:
            print("❌ Failed to send message")
            return False
            
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

def main():
    """Main function"""
    print("📊 WhatsApp Detailed Groups Analysis Sender")
    print("=" * 60)
    
    success = send_detailed_analysis_to_priority_group()
    
    if success:
        print("\n🎉 SUCCESS!")
        print("📱 Detailed analysis delivered to Priority inbox check group")
        print("📋 Individual group statuses and action items provided")
    else:
        print("\n💔 FAILED!")
        print("🔧 Please check WhatsApp bridge connection and try again")

if __name__ == "__main__":
    main() 