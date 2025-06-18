#!/usr/bin/env python3
"""
Dynamic WhatsApp Groups Analysis Script
Analyzes actual (OB) groups data to generate real-time insights
"""

import sys
import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
import re

# Add the whatsapp-mcp-server to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'whatsapp-mcp-server'))

try:
    import whatsapp
except ImportError as e:
    print(f"❌ Error importing WhatsApp module: {e}")
    sys.exit(1)

class DynamicAnalyzer:
    def __init__(self):
        self.analysis_date = datetime.now()
        self.lookback_days = 5
        self.since_date = self.analysis_date - timedelta(days=self.lookback_days)
        
        # Sentiment keywords
        self.negative_keywords = [
            'problem', 'issue', 'error', 'bug', 'fail', 'broken', 'not working',
            'crash', 'down', 'slow', 'timeout', 'refund', 'cancel', 'stop',
            'quit', 'leave', 'frustrated', 'angry', 'disappointed', 'confused',
            'stuck', 'help', 'urgent', 'critical', 'emergency', 'won\'t work',
            'doesn\'t work', 'can\'t', 'unable', 'impossible', 'terrible',
            'awful', 'worst', 'hate', 'horrible', 'useless', 'waste'
        ]
        
        self.positive_keywords = [
            'good', 'great', 'excellent', 'perfect', 'awesome', 'amazing',
            'love', 'like', 'happy', 'satisfied', 'working', 'success',
            'solved', 'fixed', 'resolved', 'thank', 'thanks', 'appreciate',
            'helpful', 'useful', 'easy', 'simple', 'smooth', 'fast',
            'quick', 'efficient', 'brilliant', 'wonderful', 'fantastic'
        ]
        
        # Internal team identifiers (phone numbers or names)
        self.internal_team = set()
        
    def get_ob_groups_direct(self) -> List[Dict[str, Any]]:
        """Get all (OB) groups directly from database"""
        try:
            import sqlite3
            db_path = os.path.join(os.path.dirname(__file__), 'whatsapp-bridge', 'store', 'messages.db')
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all OB groups
            cursor.execute("""
                SELECT jid, name, last_message_time
                FROM chats
                WHERE name LIKE '%OB%' AND jid LIKE '%@g.us'
                ORDER BY last_message_time DESC
            """)
            
            ob_groups = []
            for row in cursor.fetchall():
                jid, name, last_message_time = row
                
                # Get recent messages for this group
                cursor.execute("""
                    SELECT timestamp, sender, content, is_from_me, id
                    FROM messages
                    WHERE chat_jid = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT 100
                """, (jid, self.since_date.isoformat()))
                
                messages = []
                for msg_row in cursor.fetchall():
                    messages.append({
                        'timestamp': msg_row[0],
                        'sender': msg_row[1],
                        'content': msg_row[2] or '',
                        'is_from_me': msg_row[3],
                        'id': msg_row[4]
                    })
                
                chat_dict = {
                    'name': name,
                    'jid': jid,
                    'last_message_time': last_message_time,
                    'recent_message_count': len(messages),
                    'recent_messages': messages
                }
                ob_groups.append(chat_dict)
            
            conn.close()
            return ob_groups
            
        except Exception as e:
            print(f"❌ Error getting OB groups: {e}")
            return []
    
    def get_ob_groups(self) -> List[Dict[str, Any]]:
        """Get all (OB) groups from WhatsApp data"""
        # Use direct database access instead of the WhatsApp module
        return self.get_ob_groups_direct()
    
    def identify_internal_team_direct(self) -> None:
        """Identify internal team members from internal groups using direct DB access"""
        try:
            import sqlite3
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
            print(f"🏢 Identified {len(self.internal_team)} internal team members")
            
        except Exception as e:
            print(f"❌ Error identifying internal team: {e}")
    
    def identify_internal_team(self, all_groups: List[Any]) -> None:
        """Identify internal team members from internal groups"""
        # Use direct database access
        self.identify_internal_team_direct()
    
    def analyze_sentiment(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment of messages in a group"""
        if not messages:
            return {'sentiment_score': 0, 'total_messages': 0, 'negative_ratio': 0, 'issues': []}
        
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
            
            # Check for negative sentiment
            for keyword in self.negative_keywords:
                if keyword in content:
                    message_sentiment -= 1
                    negative_count += 1
                    # Extract potential issues
                    if any(issue_word in content for issue_word in ['error', 'problem', 'issue', 'bug', 'fail']):
                        issues.append(content[:100] + "..." if len(content) > 100 else content)
                    break
            
            # Check for positive sentiment
            if message_sentiment == 0:  # Only if not already negative
                for keyword in self.positive_keywords:
                    if keyword in content:
                        message_sentiment += 1
                        break
            
            sentiment_score += message_sentiment
        
        negative_ratio = (negative_count / total_messages * 100) if total_messages > 0 else 0
        
        return {
            'sentiment_score': sentiment_score,
            'total_messages': total_messages,
            'negative_ratio': negative_ratio,
            'issues': issues[:3]  # Top 3 issues
        }
    
    def categorize_group_status(self, sentiment_data: Dict[str, Any], message_count: int) -> Tuple[str, str]:
        """Categorize group status based on sentiment and activity"""
        negative_ratio = sentiment_data['negative_ratio']
        total_messages = sentiment_data['total_messages']
        
        # Needs Attention (Critical)
        if negative_ratio >= 25 or (negative_ratio >= 15 and total_messages >= 10):
            return "NEEDS_ATTENTION", "🔴"
        
        # At Risk (Warning)
        elif negative_ratio >= 10 or (total_messages >= 5 and sentiment_data['sentiment_score'] <= -2):
            return "AT_RISK", "🟠"
        
        # Stable
        else:
            return "STABLE", "🟢"
    
    def generate_analysis(self) -> str:
        """Generate dynamic analysis based on real data"""
        print("🔄 Generating dynamic analysis...")
        
        # Get all OB groups
        ob_groups = self.get_ob_groups()
        
        if not ob_groups:
            return "❌ No (OB) groups found or unable to access WhatsApp data"
        
        # Identify internal team members
        self.identify_internal_team([])
        
        # Analyze each group
        critical_groups = []
        at_risk_groups = []
        stable_groups = []
        
        for group in ob_groups:
            if group['recent_message_count'] == 0:
                continue  # Skip inactive groups
                
            sentiment_data = self.analyze_sentiment(group['recent_messages'])
            status, emoji = self.categorize_group_status(sentiment_data, group['recent_message_count'])
            
            group_analysis = {
                'name': group['name'],
                'jid': group['jid'],
                'status': status,
                'emoji': emoji,
                'sentiment_data': sentiment_data,
                'message_count': group['recent_message_count'],
                'last_active': group.get('last_message_time', '')
            }
            
            if status == "NEEDS_ATTENTION":
                critical_groups.append(group_analysis)
            elif status == "AT_RISK":
                at_risk_groups.append(group_analysis)
            else:
                stable_groups.append(group_analysis)
        
        # Sort by severity (negative ratio)
        critical_groups.sort(key=lambda x: x['sentiment_data']['negative_ratio'], reverse=True)
        at_risk_groups.sort(key=lambda x: x['sentiment_data']['negative_ratio'], reverse=True)
        
        # Generate report
        total_active_groups = len(critical_groups) + len(at_risk_groups) + len(stable_groups)
        
        if total_active_groups == 0:
            return "❌ No active (OB) groups found in the last 5 days"
        
        # Create dynamic message
        analysis_message = f"""📊 **LIVE (OB) GROUPS ANALYSIS - LAST {self.lookback_days} DAYS**

🎯 **Executive Summary:**
• 📊 Total Active Groups: {total_active_groups} (OB) groups with recent activity
• 🏢 Internal Team Members: {len(self.internal_team)} identified
• 📅 Analysis Period: {self.since_date.strftime('%Y-%m-%d')} to {self.analysis_date.strftime('%Y-%m-%d')}

📈 **Current Status Breakdown:**
🚨 **NEEDS ATTENTION: {len(critical_groups)} groups ({len(critical_groups)/total_active_groups*100:.1f}%)**
⚠️ **AT RISK: {len(at_risk_groups)} groups ({len(at_risk_groups)/total_active_groups*100:.1f}%)**  
✅ **STABLE: {len(stable_groups)} groups ({len(stable_groups)/total_active_groups*100:.1f}%)**

"""

        # Add critical groups section
        if critical_groups:
            analysis_message += "🚨 **TOP CRITICAL GROUPS:**\n\n"
            for i, group in enumerate(critical_groups[:5], 1):
                sentiment = group['sentiment_data']
                analysis_message += f"{i}. **{group['emoji']} {group['name']}** - {sentiment['negative_ratio']:.1f}% negative sentiment\n"
                if sentiment['issues']:
                    analysis_message += f"   • Issue: \"{sentiment['issues'][0]}\"\n"
                analysis_message += f"   • Recent activity: {sentiment['total_messages']} messages\n\n"
        
        # Add at-risk groups if any
        if at_risk_groups:
            analysis_message += "⚠️ **GROUPS AT RISK:**\n"
            for group in at_risk_groups[:3]:
                sentiment = group['sentiment_data']
                analysis_message += f"• **{group['name']}** - {sentiment['negative_ratio']:.1f}% negative sentiment ({sentiment['total_messages']} messages)\n"
            analysis_message += "\n"
        
        # Action plan based on real data
        analysis_message += "🎯 **IMMEDIATE ACTION PLAN:**\n\n"
        
        if critical_groups:
            analysis_message += "**Priority 1 (Next 2 Hours):**\n"
            for group in critical_groups[:3]:
                analysis_message += f"• Contact {group['name']} - Address {group['sentiment_data']['negative_ratio']:.0f}% negative sentiment\n"
            analysis_message += "\n"
        
        if at_risk_groups:
            analysis_message += "**Priority 2 (Next 8 Hours):**\n"
            for group in at_risk_groups[:3]:
                analysis_message += f"• Monitor {group['name']} - Watch for escalation\n"
            analysis_message += "\n"
        
        analysis_message += "**Priority 3 (Next 24 Hours):**\n"
        analysis_message += "• Review stable groups for any emerging issues\n"
        analysis_message += "• Maintain response time standards\n"
        analysis_message += "• Update internal team recognition\n\n"
        
        # Success metrics
        stable_percentage = len(stable_groups)/total_active_groups*100
        analysis_message += "✨ **Current Metrics:**\n"
        analysis_message += f"• {stable_percentage:.1f}% of groups are stable\n"
        analysis_message += f"• {len(self.internal_team)} internal team members identified\n"
        analysis_message += f"• Real-time sentiment analysis active\n"
        analysis_message += f"• {sum(g['message_count'] for g in critical_groups + at_risk_groups + stable_groups)} total messages analyzed\n\n"
        
        analysis_message += f"Generated: {self.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}"
        
        return analysis_message

def main():
    """Main function to generate and return dynamic analysis"""
    try:
        analyzer = DynamicAnalyzer()
        analysis = analyzer.generate_analysis()
        print("✅ Dynamic analysis generated successfully")
        return analysis
    except Exception as e:
        print(f"❌ Error generating dynamic analysis: {e}")
        return f"❌ Failed to generate dynamic analysis: {str(e)}"

if __name__ == "__main__":
    result = main()
    print("\n" + "="*80)
    print(result)