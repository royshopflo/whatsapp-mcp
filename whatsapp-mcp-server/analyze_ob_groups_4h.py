import sqlite3
import re
from datetime import datetime, timedelta, time
from typing import List, Dict, Any, Tuple
import pytz

# Constants
OB_GROUP_SEARCH_TERM = "(OB)"
DAYS_TO_ANALYZE = 5
DB_PATH = "../whatsapp-bridge/store/messages.db"
SLA_HOURS = 4  # 4-hour SLA in hours
IST_TIMEZONE = pytz.timezone('Asia/Kolkata')

# Define working hours in IST
WORK_HOURS_START = time(10, 0)  # 10:00 AM IST
WORK_HOURS_END = time(19, 0)    # 7:00 PM IST

# Negative sentiment keywords
NEGATIVE_KEYWORDS = [
    r"annoyed", r"angry", r"disappointed", r"sad", r"frustrated", r"upset", 
    r"not happy", r"bad experience", r"unhappy", r"issue", r"problem", 
    r"complain", r"complaint", r"delay", r"waiting", r"no response", 
    r"not working", r"doesn't work", r"does not work", r"fail", r"failed",
    r"broken", r"error", r"bug", r"glitch", r"terrible", r"horrible",
    r"awful", r"waste", r"poor", r"bad", r"worst", r"hate", r"dissatisfied",
    r"refund", r"money back", r"cancel", r"cancellation", r"not satisfied",
    r"urgent", r"ASAP", r"critical", r"immediate", r"unresolved"
]

# Urgent language patterns
URGENT_PATTERNS = [
    r"immediate", r"ASAP", r"urgent", r"critical", r"right away", r"right now",
    r"as soon as", r"emergency", r"priority", r"escalate", r"escalation"
]

# Multiple punctuation patterns
EMPHASIS_PATTERNS = [
    r"!{2,}", r"\?{2,}", r"[A-Z]{3,}"  # Multiple exclamation/question marks or ALL CAPS
]

def is_within_working_hours(timestamp_str: str) -> bool:
    """Check if a timestamp falls within working hours (10AM-7PM IST)"""
    try:
        # Parse the timestamp - format is like "2025-05-21 10:56:09+05:30"
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S%z")
        
        # Convert to IST if needed
        if dt.tzinfo is not None:
            ist_dt = dt.astimezone(IST_TIMEZONE)
        else:
            # If no timezone, assume it's in local time and add IST timezone
            ist_dt = IST_TIMEZONE.localize(dt)
            
        # Check if it's within working hours
        current_time = ist_dt.time()
        return WORK_HOURS_START <= current_time <= WORK_HOURS_END
    
    except ValueError as e:
        print(f"Error parsing timestamp '{timestamp_str}': {e}")
        return True  # Default to working hours if parsing fails

def find_ob_groups() -> List[Dict[str, Any]]:
    """Find all WhatsApp groups with (OB) in their name"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Query for groups with (OB) in their name
        cursor.execute("""
            SELECT jid, name, last_message_time
            FROM chats
            WHERE name LIKE ? AND jid LIKE '%@g.us'
            ORDER BY last_message_time DESC
        """, (f'%{OB_GROUP_SEARCH_TERM}%',))
        
        groups = []
        for row in cursor.fetchall():
            groups.append({
                'jid': row[0],
                'name': row[1],
                'last_message_time': row[2] if row[2] else None
            })
        
        return groups
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

def get_recent_messages(chat_jid: str, days: int = DAYS_TO_ANALYZE) -> List[Dict[str, Any]]:
    """Get messages from the specified chat from the last DAYS_TO_ANALYZE days"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Calculate cutoff date in the format the database uses
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        # Query for messages
        query = """
            SELECT timestamp, sender, content, is_from_me, id
            FROM messages
            WHERE chat_jid = ? AND timestamp >= ?
            ORDER BY timestamp ASC
            LIMIT 500
        """
        
        cursor.execute(query, (chat_jid, cutoff_date))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'timestamp': row[0],
                'sender': row[1],
                'content': row[2],
                'is_from_me': bool(row[3]),
                'id': row[4]
            })
        
        if messages:
            print(f"Found {len(messages)} messages in the last {days} days")
        
        return messages
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

def has_emphasis_patterns(text: str) -> bool:
    """Check if text contains emphasis patterns like !!!, ???, ALL CAPS"""
    for pattern in EMPHASIS_PATTERNS:
        if re.search(pattern, text):
            return True
    return False

def has_urgent_language(text: str) -> bool:
    """Check if text contains urgent language patterns"""
    for pattern in URGENT_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def has_negative_sentiment(text: str) -> Tuple[bool, str]:
    """Check if text contains negative sentiment keywords"""
    for keyword in NEGATIVE_KEYWORDS:
        if re.search(keyword, text, re.IGNORECASE):
            return True, keyword
    return False, ""

def calculate_response_times(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calculate response times between merchant messages and Shopflo responses"""
    delayed_responses = []
    merchant_queries = []
    last_merchant_msg = None
    
    for i, msg in enumerate(messages):
        if not msg.get('content'):
            continue
            
        is_from_merchant = not msg.get('is_from_me', False)
        
        if is_from_merchant:
            last_merchant_msg = msg
            merchant_queries.append(msg)
        elif last_merchant_msg is not None:
            try:
                # Calculate response time
                merchant_time = datetime.strptime(last_merchant_msg['timestamp'], "%Y-%m-%d %H:%M:%S%z")
                response_time = datetime.strptime(msg['timestamp'], "%Y-%m-%d %H:%M:%S%z")
                response_delta = response_time - merchant_time
                response_minutes = response_delta.total_seconds() / 60
                response_hours = response_minutes / 60
                
                # Check if response time exceeds SLA during working hours
                if is_within_working_hours(last_merchant_msg['timestamp']) and response_hours > SLA_HOURS:
                    delayed_responses.append({
                        'merchant_message': last_merchant_msg,
                        'response_message': msg,
                        'response_hours': response_hours,
                        'timestamp': last_merchant_msg['timestamp']
                    })
                    print(f"Found delayed response: {response_hours:.1f} hours")
                
                # Reset merchant message after finding a response
                merchant_queries.pop()
                last_merchant_msg = None if not merchant_queries else merchant_queries[-1]
                
            except ValueError as e:
                print(f"Error calculating response time: {e}")
    
    # Check for unanswered queries (merchant messages without responses)
    unanswered_queries = []
    for query in merchant_queries:
        unanswered_queries.append({
            'merchant_message': query,
            'timestamp': query['timestamp']
        })
    
    return delayed_responses, unanswered_queries

def analyze_sentiment_emphasis(messages: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Analyze sentiment, urgent language, and emphasis patterns in messages"""
    negative_messages = []
    urgent_messages = []
    emphasis_messages = []
    
    for msg in messages:
        content = msg.get('content', '')
        if not content or msg.get('is_from_me', False):
            continue
            
        # Check for negative sentiment
        has_negative, keyword = has_negative_sentiment(content)
        if has_negative:
            negative_messages.append({
                'timestamp': msg.get('timestamp'),
                'content': content,
                'keyword': keyword
            })
        
        # Check for urgent language
        if has_urgent_language(content):
            urgent_messages.append({
                'timestamp': msg.get('timestamp'),
                'content': content
            })
        
        # Check for emphasis patterns
        if has_emphasis_patterns(content):
            emphasis_messages.append({
                'timestamp': msg.get('timestamp'),
                'content': content
            })
    
    return negative_messages, urgent_messages, emphasis_messages

def classify_merchant(
    negative_messages: List[Dict[str, Any]], 
    urgent_messages: List[Dict[str, Any]],
    emphasis_messages: List[Dict[str, Any]],
    delayed_responses: List[Dict[str, Any]],
    unanswered_queries: List[Dict[str, Any]]
) -> str:
    """Classify merchant based on sentiment and response analysis"""
    
    # Check for "Needs Attention" criteria
    if (negative_messages and (urgent_messages or emphasis_messages)) or len(unanswered_queries) > 1:
        return "Needs Attention"
    
    # Check for "At Risk" criteria
    if delayed_responses or negative_messages or unanswered_queries:
        return "At Risk"
    
    # Default to "Stable"
    return "Stable"

def analyze_ob_groups() -> Dict[str, Dict[str, Any]]:
    """Main function to analyze all OB groups"""
    results = {}
    
    # Find all OB groups
    ob_groups = find_ob_groups()
    print(f"Found {len(ob_groups)} groups with (OB) in their name")
    
    # For each group, get messages and classify
    for group in ob_groups:
        group_jid = group.get('jid')
        group_name = group.get('name', group_jid)
        
        print(f"\nAnalyzing group: {group_name}")
        
        try:
            # Get messages from last 5 days
            messages = get_recent_messages(group_jid)
            
            # Analyze sentiment, urgent language, and emphasis patterns
            negative_messages, urgent_messages, emphasis_messages = analyze_sentiment_emphasis(messages)
            
            # Calculate response times and find unanswered queries
            delayed_responses, unanswered_queries = calculate_response_times(messages)
            
            # Classify the merchant
            classification = classify_merchant(
                negative_messages, urgent_messages, emphasis_messages,
                delayed_responses, unanswered_queries
            )
            
            # Store results
            results[group_name] = {
                'classification': classification,
                'message_count': len(messages),
                'jid': group_jid,
                'negative_messages': negative_messages,
                'urgent_messages': urgent_messages,
                'emphasis_messages': emphasis_messages,
                'delayed_responses': delayed_responses,
                'unanswered_queries': unanswered_queries
            }
            
            print(f"Classification: {classification}")
            
        except Exception as e:
            print(f"Error analyzing group {group_name}: {e}")
            results[group_name] = {
                'classification': 'Error',
                'error_message': str(e),
                'jid': group_jid
            }
    
    return results

def generate_markdown_report(results: Dict[str, Dict[str, Any]]) -> str:
    """Generate a markdown report of the analysis results"""
    # Count groups in each category
    needs_attention_count = sum(1 for details in results.values() 
                               if details.get('classification') == 'Needs Attention')
    at_risk_count = sum(1 for details in results.values() 
                       if details.get('classification') == 'At Risk')
    stable_count = sum(1 for details in results.values() 
                      if details.get('classification') == 'Stable')
    error_count = sum(1 for details in results.values() 
                     if details.get('classification') == 'Error')
    total_count = needs_attention_count + at_risk_count + stable_count + error_count
    
    # Calculate percentages
    needs_attention_pct = (needs_attention_count / total_count * 100) if total_count > 0 else 0
    at_risk_pct = (at_risk_count / total_count * 100) if total_count > 0 else 0
    stable_pct = (stable_count / total_count * 100) if total_count > 0 else 0
    
    # Generate report header
    report = f"""# WhatsApp OB Group Analysis Report

## Summary Statistics

**Analysis Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Period Analyzed:** Last {DAYS_TO_ANALYZE} days  
**Total Groups Analyzed:** {total_count}  
**SLA Criterion:** {SLA_HOURS} hours response time during working hours (10AM-7PM IST)

| Classification | Count | Percentage |
|----------------|-------|------------|
| Needs Attention (High Priority) | {needs_attention_count} | {needs_attention_pct:.1f}% |
| At Risk (Medium Priority) | {at_risk_count} | {at_risk_pct:.1f}% |
| Stable (Low Priority) | {stable_count} | {stable_pct:.1f}% |
| Error | {error_count} | {(error_count / total_count * 100) if total_count > 0 else 0:.1f}% |

## Classification Criteria

1. **Needs Attention (High Priority):**
   - Merchant expresses clear negative emotions: frustration, anger, disappointment
   - Uses phrases like "not working," "issue," "problem," "waiting for," "unresolved"
   - Contains urgent language: "immediate," "ASAP," "urgent," "critical"
   - Multiple follow-up messages without Shopflo response
   - Uses exclamation marks, ALL CAPS, or multiple question marks

2. **At Risk (Medium Priority):**
   - Shopflo response time exceeds {SLA_HOURS} hours during business hours
   - Merchant has followed up at least once before receiving a response
   - Mild expressions of concern or confusion
   - Questions remain partially answered

3. **Stable (Low Priority):**
   - Positive or neutral sentiment in messages
   - Timely responses from Shopflo team (within {SLA_HOURS} hours during business hours)
   - Questions fully addressed
   - No unresolved issues mentioned

"""

    # Add detailed section for merchants needing attention
    if needs_attention_count > 0:
        report += "## Merchants Needing Attention\n\n"
        for group_name, details in results.items():
            if details.get('classification') == 'Needs Attention':
                report += f"### {group_name}\n"
                report += f"- **Message Count:** {details.get('message_count', 0)}\n"
                
                # Add negative messages
                negative_messages = details.get('negative_messages', [])
                if negative_messages:
                    report += f"- **Negative Sentiment Issues:** {len(negative_messages)}\n"
                    report += "  - Examples:\n"
                    for i, msg in enumerate(negative_messages[:2]):
                        timestamp = msg.get('timestamp', '')
                        keyword = msg.get('keyword', '')
                        content = msg.get('content', '')[:100] + "..."
                        report += f"    - \"{content}\" (Keyword: {keyword}, {timestamp})\n"
                
                # Add urgent messages
                urgent_messages = details.get('urgent_messages', [])
                if urgent_messages:
                    report += f"- **Urgent Requests:** {len(urgent_messages)}\n"
                
                # Add unanswered queries
                unanswered_queries = details.get('unanswered_queries', [])
                if unanswered_queries:
                    report += f"- **Unanswered Messages:** {len(unanswered_queries)}\n"
                    if len(unanswered_queries) > 0:
                        latest = unanswered_queries[-1].get('merchant_message', {})
                        content = latest.get('content', '')[:100] + "..."
                        timestamp = latest.get('timestamp', '')
                        report += f"  - Latest: \"{content}\" ({timestamp})\n"
                
                report += "\n"
    
    # Add detailed section for at-risk merchants
    if at_risk_count > 0:
        report += "## At-Risk Merchants\n\n"
        for group_name, details in results.items():
            if details.get('classification') == 'At Risk':
                report += f"### {group_name}\n"
                report += f"- **Message Count:** {details.get('message_count', 0)}\n"
                
                # Add delayed responses
                delayed_responses = details.get('delayed_responses', [])
                if delayed_responses:
                    report += f"- **Delayed Responses:** {len(delayed_responses)}\n"
                    report += "  - Examples:\n"
                    for i, response in enumerate(delayed_responses[:2]):
                        hours = response.get('response_hours', 0)
                        timestamp = response.get('timestamp', '')
                        msg = response.get('merchant_message', {}).get('content', '')[:100] + "..."
                        report += f"    - {hours:.1f} hours to respond to \"{msg}\" ({timestamp})\n"
                
                # Add negative messages if present (but not enough for "Needs Attention")
                negative_messages = details.get('negative_messages', [])
                if negative_messages:
                    report += f"- **Mild Concern Issues:** {len(negative_messages)}\n"
                
                report += "\n"
    
    # Add recommendations
    report += """## Recommendations for Immediate Follow-Up Actions

### For "Needs Attention" Merchants
1. **Immediate Response Required:**
   - Assign dedicated support personnel to each high-priority merchant
   - Respond to all unanswered messages within 1 hour
   - Schedule follow-up calls for merchants with urgent issues

2. **Technical Escalation:**
   - Escalate technical issues to specialized teams
   - Provide temporary workarounds while permanent solutions are developed
   - Keep merchants informed about resolution progress

### For "At Risk" Merchants
1. **Proactive Outreach:**
   - Check in with merchants who have experienced delayed responses
   - Follow up on partially resolved issues
   - Offer additional assistance or training if needed

2. **Response Time Improvement:**
   - Ensure all messages are answered within the 4-hour SLA
   - Set up monitoring for approaching SLA breaches
   - Provide status updates even if complete resolution is not immediately available

### System-Level Improvements
1. **Support Process Optimization:**
   - Develop templates for common issues to speed up response times
   - Implement alert system for messages approaching SLA threshold
   - Create knowledge base for frequently encountered problems

2. **Monitoring Enhancement:**
   - Continue regular sentiment analysis of conversations
   - Track SLA compliance rates by time of day and day of week
   - Establish dashboard for real-time monitoring of high-priority conversations

---

*Report generated on {datetime.now().strftime('%Y-%m-%d')} analyzing {DAYS_TO_ANALYZE} days of WhatsApp conversations*
"""

    return report

def save_report_to_file(report: str, filename: str = "merchant_analysis_report.md") -> None:
    """Save the report to a markdown file"""
    with open(filename, 'w') as f:
        f.write(report)
    print(f"Report saved to {filename}")

if __name__ == "__main__":
    try:
        # Check if pytz is installed
        import pytz
    except ImportError:
        print("The pytz module is required. Please install it using 'pip install pytz'")
        import sys
        sys.exit(1)

    # Run actual analysis
    results = analyze_ob_groups()
    
    # Generate and save the markdown report
    report = generate_markdown_report(results)
    save_report_to_file(report)
    
    # Print summary statistics
    needs_attention = sum(1 for d in results.values() if d.get('classification') == 'Needs Attention')
    at_risk = sum(1 for d in results.values() if d.get('classification') == 'At Risk')
    stable = sum(1 for d in results.values() if d.get('classification') == 'Stable')
    
    print("\n===== ANALYSIS SUMMARY =====")
    print(f"Analyzed {len(results)} OB groups over the last {DAYS_TO_ANALYZE} days")
    print(f"Needs Attention (High Priority): {needs_attention}")
    print(f"At Risk (Medium Priority): {at_risk}")
    print(f"Stable (Low Priority): {stable}")
    print("==============================") 