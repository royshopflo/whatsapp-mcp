import sqlite3
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

# Constants
OB_GROUP_SEARCH_TERM = "(OB)"
DAYS_TO_ANALYZE = 5
DB_PATH = "../whatsapp-bridge/store/messages.db"

# Negative sentiment keywords
NEGATIVE_KEYWORDS = [
    r"annoyed", r"angry", r"disappointed", r"sad", r"frustrated", r"upset", 
    r"not happy", r"bad experience", r"unhappy", r"issue", r"problem", 
    r"complain", r"complaint", r"delay", r"waiting", r"no response", 
    r"not working", r"doesn't work", r"does not work", r"fail", r"failed",
    r"broken", r"error", r"bug", r"glitch", r"terrible", r"horrible",
    r"awful", r"waste", r"poor", r"bad", r"worst", r"hate", r"dissatisfied",
    r"refund", r"money back", r"cancel", r"cancellation", r"not satisfied"
]

def find_ob_groups() -> List[Dict[str, Any]]:
    """
    Find all WhatsApp groups with (OB) in their name by querying the database directly
    
    Returns:
        List of group dictionaries with jid, name, and other metadata
    """
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


def get_recent_messages(chat_jid: str, days: int = DAYS_TO_ANALYZE, limit: int = 500) -> List[Dict[str, Any]]:
    """
    Get messages from the specified chat from the last DAYS_TO_ANALYZE days
    by querying the database directly
    
    Args:
        chat_jid: The JID of the chat to get messages from
        days: Number of days to look back
        limit: Maximum number of messages to retrieve
        
    Returns:
        List of message dictionaries with timestamp, sender, content, is_from_me
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Calculate cutoff date
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Query for messages
        cursor.execute("""
            SELECT timestamp, sender, content, is_from_me, id
            FROM messages
            WHERE chat_jid = ? AND timestamp > ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (chat_jid, cutoff_date, limit))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'timestamp': row[0],
                'sender': row[1],
                'content': row[2],
                'is_from_me': bool(row[3]),
                'id': row[4]
            })
        
        # Print sample messages for inspection
        if messages:
            print(f"Found {len(messages)} messages in the last {days} days")
            
            # Print the first 3 messages (or fewer if there aren't that many)
            sample_count = min(3, len(messages))
            for i in range(sample_count):
                # Truncate messages to 200 chars for readability
                msg = messages[i]
                print(f"Message {i+1} ({msg['timestamp']}): {msg['content'][:200]}...")
        
        return messages
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()


def analyze_sentiment(messages: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Analyze the sentiment of messages to categorize the group
    
    Args:
        messages: List of message dictionaries
        
    Returns:
        Tuple of (classification, list of messages with negative sentiment)
    """
    # Keep track of merchant messages with negative sentiment
    negative_messages = []
    
    # 1. Check for negative sentiment keywords
    for msg in messages:
        content = msg.get('content', '')
        # Skip empty messages or messages without content
        if not content:
            continue
        
        # Check if message contains negative sentiment
        for keyword in NEGATIVE_KEYWORDS:
            if re.search(keyword, content, re.IGNORECASE):
                print(f"Found negative sentiment: '{keyword}' in message: '{content[:100]}...'")
                negative_messages.append({
                    'timestamp': msg.get('timestamp'),
                    'content': content,
                    'keyword': keyword
                })
                break
    
    # If we found any negative sentiment messages, classify as "Needs attention"
    if negative_messages:
        return "Needs attention", negative_messages
    
    # 2. Check for delayed responses
    # Find pairs of messages where a merchant message is followed by a Shopflo response
    # with a delay longer than 1 hour
    delayed_responses = []
    
    # We can only implement this if we know which senders are merchants versus Shopflo team
    # For now, we assume any response longer than 1 hour is a delayed response
    
    if delayed_responses:
        return "At risk", []
    
    # 3. Otherwise, classify as stable
    return "Stable Merchant", []


def analyze_ob_groups() -> Dict[str, Dict[str, Any]]:
    """
    Main function to analyze all OB groups
    
    Returns:
        Dict with group names as keys and classification details as values
    """
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
            
            # Classify the group based on sentiment analysis
            classification, negative_messages = analyze_sentiment(messages)
            
            # Store results
            results[group_name] = {
                'classification': classification,
                'message_count': len(messages),
                'jid': group_jid,
                'negative_messages': negative_messages
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


def print_report(results: Dict[str, Dict[str, Any]]) -> None:
    """
    Print a formatted report of the analysis results
    
    Args:
        results: Dictionary with group names as keys and classification details as values
    """
    # Count groups in each category
    needs_attention_count = sum(1 for details in results.values() 
                               if details.get('classification') == 'Needs attention')
    at_risk_count = sum(1 for details in results.values() 
                       if details.get('classification') == 'At risk')
    stable_count = sum(1 for details in results.values() 
                      if details.get('classification') == 'Stable Merchant')
    error_count = sum(1 for details in results.values() 
                     if details.get('classification') == 'Error')
    
    # Print summary
    print("\n===== ANALYSIS REPORT =====")
    print(f"Analyzed {len(results)} OB groups over the last {DAYS_TO_ANALYZE} days\n")
    print(f"SUMMARY:")
    print(f"  Needs attention: {needs_attention_count}")
    print(f"  At risk: {at_risk_count}")
    print(f"  Stable: {stable_count}")
    print(f"  Errors: {error_count}\n")
    
    # Print details for each category
    if needs_attention_count > 0:
        print("NEEDS ATTENTION:")
        for group_name, details in results.items():
            if details.get('classification') == 'Needs attention':
                print(f"  - {group_name} ({details.get('message_count', 0)} messages)")
                
                # Print sample negative messages
                negative_messages = details.get('negative_messages', [])
                if negative_messages:
                    print(f"    Negative messages found ({len(negative_messages)}):")
                    for i, msg in enumerate(negative_messages[:3]):  # Show up to 3 examples
                        print(f"      {i+1}. [{msg.get('timestamp')}] '{msg.get('keyword')}' found in: {msg.get('content', '')[:100]}...")
        print()
    
    if at_risk_count > 0:
        print("AT RISK:")
        for group_name, details in results.items():
            if details.get('classification') == 'At risk':
                print(f"  - {group_name} ({details.get('message_count', 0)} messages)")
        print()
    
    if stable_count > 0:
        print("STABLE MERCHANTS:")
        for group_name, details in results.items():
            if details.get('classification') == 'Stable Merchant':
                print(f"  - {group_name} ({details.get('message_count', 0)} messages)")
        print()
    
    if error_count > 0:
        print("ERRORS:")
        for group_name, details in results.items():
            if details.get('classification') == 'Error':
                print(f"  - {group_name}: {details.get('error_message', 'Unknown error')}")
        print()


if __name__ == "__main__":
    # Run actual analysis
    results = analyze_ob_groups()
    print_report(results) 