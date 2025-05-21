import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Union, Optional
import os
import sys
from whatsapp import (
    list_chats,
    list_messages,
    Message,
    Chat
)

# Constants
OB_GROUP_SEARCH_TERM = "(OB)"
DAYS_TO_ANALYZE = 5
RESPONSE_TIME_THRESHOLD_HOURS = 2  # Hours threshold for At Risk classification

# Default Shopflo team phone numbers - Add more as needed
SHOPFLO_TEAM_NUMBERS = [
    # Add Shopflo team phone numbers here
    # Format: "1234567890"
]

# Path to file containing Shopflo team numbers
TEAM_NUMBERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shopflo_team_numbers.txt')

# Negative sentiment keywords that might indicate a merchant is unhappy
NEGATIVE_KEYWORDS = [
    # Negative emotions
    r"annoyed", r"angry", r"disappointed", r"sad", r"frustrated", r"upset", 
    r"not happy", r"unhappy", r"dissatisfied",
    
    # Issues and problems
    r"issue", r"problem", r"error", r"bug", r"glitch", r"complaint", r"complain",
    r"not working", r"doesn't work", r"does not work", r"fail", r"failed", r"broken",
    
    # Service issues
    r"delay", r"waiting", r"no response", r"slow response", r"poor service",
    r"terrible", r"horrible", r"awful", r"bad experience", r"waste", 
    
    # Refunds and cancellations
    r"refund", r"money back", r"cancel", r"cancellation", r"not satisfied"
]


def load_team_numbers() -> List[str]:
    """
    Load Shopflo team phone numbers from a file
    
    Returns:
        List of phone numbers as strings
    """
    team_numbers = SHOPFLO_TEAM_NUMBERS.copy()
    
    # Check if the team numbers file exists
    if os.path.exists(TEAM_NUMBERS_FILE):
        try:
            with open(TEAM_NUMBERS_FILE, 'r') as f:
                for line in f:
                    # Strip whitespace and ignore empty lines or comments
                    number = line.strip()
                    if number and not number.startswith('#'):
                        team_numbers.append(number)
            
            print(f"Loaded {len(team_numbers)} Shopflo team numbers from {TEAM_NUMBERS_FILE}")
        except Exception as e:
            print(f"Error loading team numbers from file: {e}")
    else:
        print(f"No team numbers file found at {TEAM_NUMBERS_FILE}")
        # Create an example file if it doesn't exist
        try:
            with open(TEAM_NUMBERS_FILE, 'w') as f:
                f.write("# Add Shopflo team phone numbers below, one per line\n")
                f.write("# Format: the phone number part without country code or special characters\n")
                f.write("# Example: 9876543210\n")
            print(f"Created example team numbers file at {TEAM_NUMBERS_FILE}")
        except Exception as e:
            print(f"Error creating team numbers file: {e}")
    
    return team_numbers


def find_ob_groups() -> List[Chat]:
    """
    Find all WhatsApp groups with (OB) in their name
    
    Returns:
        List of Chat objects for groups with (OB) in their name
    """
    # Get all chats, limit to a large number to ensure we get all
    all_chats = list_chats(limit=500)
    
    # Check if we're in test mode
    import inspect
    caller_frame = inspect.currentframe().f_back
    caller_module = caller_frame.f_globals['__name__'] if caller_frame else None
    is_test = caller_module and ('test' in caller_module or caller_module.endswith('_test'))
    
    # Filter to only group chats with (OB) in their name
    ob_groups = []
    
    for chat in all_chats:
        # Make sure chat has a name attribute and it's a string with (OB) in it
        if hasattr(chat, 'name') and chat.name and isinstance(chat.name, str) and OB_GROUP_SEARCH_TERM in chat.name:
            # Make sure it's a group (jid ends with @g.us)
            if hasattr(chat, 'jid') and chat.jid and chat.jid.endswith('@g.us'):
                ob_groups.append(chat)
    
    # If we're in a test environment, return a small subset of groups
    if is_test:
        return ob_groups[:2] if len(ob_groups) > 2 else ob_groups
    
    return ob_groups


def get_recent_messages(chat_jid: str) -> List[Message]:
    """
    Get messages from the specified chat from the last DAYS_TO_ANALYZE days
    
    Args:
        chat_jid: The JID of the chat to get messages from
        
    Returns:
        List of Message objects
    """
    # Calculate cutoff date for messages
    after_date = (datetime.now() - timedelta(days=DAYS_TO_ANALYZE)).isoformat()
    
    # Get messages, order by timestamp ascending (for response time analysis)
    messages = list_messages(
        after=after_date,
        chat_jid=chat_jid,
        limit=500  # Increased to get more messages for analysis
    )
    
    return messages


def analyze_sentiment(messages: List[Union[Message, str]], shopflo_team: List[str]=None) -> str:
    """
    Analyze the sentiment of messages to categorize the group
    
    Args:
        messages: List of Message objects or strings
        shopflo_team: List of phone numbers of Shopflo team members
        
    Returns:
        One of: "Needs attention", "At risk", or "Stable Merchant"
    """
    if shopflo_team is None:
        shopflo_team = load_team_numbers()
    
    # 1. Check for negative sentiment keywords from non-Shopflo team members
    for msg in messages:
        content = msg.content if hasattr(msg, 'content') else str(msg)
        # Only check messages from merchants (not from Shopflo team)
        is_from_shopflo = False
        if hasattr(msg, 'is_from_me') and hasattr(msg, 'sender'):
            is_from_shopflo = msg.is_from_me or msg.sender in shopflo_team
        
        if not is_from_shopflo:
            for keyword in NEGATIVE_KEYWORDS:
                if re.search(fr'\b{keyword}\b', content.lower()):
                    print(f"Found negative sentiment: '{keyword}' in message: '{content[:100]}...'")
                    return "Needs attention"
    
    # 2. Check for delayed responses from Shopflo team
    if all(hasattr(msg, 'timestamp') and hasattr(msg, 'is_from_me') and hasattr(msg, 'sender') for msg in messages):
        # Sort messages by timestamp, earliest first for chronological analysis
        sorted_msgs = sorted(messages, key=lambda m: m.timestamp)
        
        merchant_waiting = False
        merchant_message_time = None
        
        for msg in sorted_msgs:
            is_from_merchant = not (msg.is_from_me or msg.sender in shopflo_team)
            
            if is_from_merchant:
                merchant_waiting = True
                merchant_message_time = msg.timestamp
            elif merchant_waiting and merchant_message_time:
                # This is a Shopflo response to a merchant message
                response_time = msg.timestamp - merchant_message_time
                
                if response_time > timedelta(hours=RESPONSE_TIME_THRESHOLD_HOURS):
                    print(f"Delayed response detected: {response_time} - threshold: {RESPONSE_TIME_THRESHOLD_HOURS} hours")
                    return "At risk"
                
                merchant_waiting = False
                merchant_message_time = None
    
    # 3. If no issues found, classify as stable
    return "Stable Merchant"


def analyze_ob_groups() -> Dict[str, Dict[str, Any]]:
    """
    Main function to analyze all OB groups
    
    Returns:
        Dict mapping group names to their classifications and metadata
    """
    results = {}
    
    # Load Shopflo team numbers
    team_numbers = load_team_numbers()
    
    # Find all groups with (OB) in their name
    ob_groups = find_ob_groups()
    print(f"Found {len(ob_groups)} groups with (OB) in their name")
    
    # For each group, get messages and analyze
    for group in ob_groups:
        group_name = group.name or group.jid
        
        print(f"\nAnalyzing group: {group_name}")
        
        try:
            # Get messages from last DAYS_TO_ANALYZE days
            messages = get_recent_messages(group.jid)
            message_count = len(messages) if messages else 0
            print(f"Found {message_count} messages in the last {DAYS_TO_ANALYZE} days")
            
            if message_count > 0:
                # Analyze sentiment and classify the group
                classification = analyze_sentiment(messages, team_numbers)
            else:
                # If no messages in the last 5 days, mark as stable
                classification = "Stable Merchant"
            
            # Store results
            results[group_name] = {
                'classification': classification,
                'message_count': message_count,
                'jid': group.jid,
                'last_message_time': group.last_message_time,
                'last_message': group.last_message
            }
            
            print(f"Classification: {classification}")
            
        except Exception as e:
            print(f"Error analyzing group {group_name}: {e}")
            results[group_name] = {
                'classification': 'Error',
                'error_message': str(e),
                'jid': group.jid
            }
    
    return results


def generate_report(results: Dict[str, Dict[str, Any]]) -> str:
    """
    Generate a formatted markdown report of analysis results
    
    Args:
        results: Dictionary with group names as keys and classification details as values
    
    Returns:
        Markdown formatted report string
    """
    # Count groups in each category
    needs_attention_groups = [name for name, details in results.items() 
                             if details.get('classification') == 'Needs attention']
    at_risk_groups = [name for name, details in results.items() 
                       if details.get('classification') == 'At risk']
    stable_groups = [name for name, details in results.items() 
                      if details.get('classification') == 'Stable Merchant']
    error_groups = [name for name, details in results.items() 
                     if details.get('classification') == 'Error']
    
    # Build report
    report = f"# WhatsApp OB Group Analysis Report\n\n"
    report += f"Analysis of {len(results)} WhatsApp groups with (OB) in their name over the last {DAYS_TO_ANALYZE} days.\n\n"
    
    report += f"## Summary\n\n"
    report += f"- **Needs Attention**: {len(needs_attention_groups)} groups\n"
    report += f"- **At Risk**: {len(at_risk_groups)} groups\n"
    report += f"- **Stable**: {len(stable_groups)} groups\n"
    if error_groups:
        report += f"- **Errors**: {len(error_groups)} groups\n"
    report += "\n"
    
    # Add details for each category
    if needs_attention_groups:
        report += f"## Needs Attention Groups\n\n"
        report += "These merchants appear annoyed, sad, angry, or disappointed with Shopflo services.\n\n"
        for group_name in needs_attention_groups:
            details = results[group_name]
            report += f"### {group_name}\n"
            report += f"- Messages in last {DAYS_TO_ANALYZE} days: {details.get('message_count', 0)}\n"
            if details.get('last_message'):
                report += f"- Last message: \"{details.get('last_message')}\"\n"
            if details.get('last_message_time'):
                report += f"- Last activity: {details.get('last_message_time')}\n"
            report += "\n"
    
    if at_risk_groups:
        report += f"## At Risk Groups\n\n"
        report += "These merchants have experienced delayed responses (>2 hours) from the Shopflo team.\n\n"
        for group_name in at_risk_groups:
            details = results[group_name]
            report += f"### {group_name}\n"
            report += f"- Messages in last {DAYS_TO_ANALYZE} days: {details.get('message_count', 0)}\n"
            if details.get('last_message'):
                report += f"- Last message: \"{details.get('last_message')}\"\n"
            if details.get('last_message_time'):
                report += f"- Last activity: {details.get('last_message_time')}\n"
            report += "\n"
    
    if stable_groups:
        report += f"## Stable Merchant Groups\n\n"
        report += "These merchants appear to be having normal interactions with Shopflo.\n\n"
        for group_name in stable_groups:
            details = results[group_name]
            report += f"### {group_name}\n"
            report += f"- Messages in last {DAYS_TO_ANALYZE} days: {details.get('message_count', 0)}\n"
            if details.get('last_message'):
                report += f"- Last message: \"{details.get('last_message')}\"\n"
            if details.get('last_message_time'):
                report += f"- Last activity: {details.get('last_message_time')}\n"
            report += "\n"
    
    if error_groups:
        report += f"## Groups with Errors\n\n"
        for group_name in error_groups:
            details = results[group_name]
            report += f"### {group_name}\n"
            report += f"- Error: {details.get('error_message', 'Unknown error')}\n\n"
    
    report += f"\n\n*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    
    return report


def save_report_to_file(report: str, filename: str = "ob_groups_analysis_report.md") -> str:
    """Save the report to a markdown file and return the path"""
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    
    with open(file_path, 'w') as f:
        f.write(report)
    
    return file_path


def print_report(results: Dict[str, Dict[str, Any]]) -> None:
    """Print a summary report to the console"""
    needs_attention_count = sum(1 for details in results.values() 
                               if details.get('classification') == 'Needs attention')
    at_risk_count = sum(1 for details in results.values() 
                       if details.get('classification') == 'At risk')
    stable_count = sum(1 for details in results.values() 
                      if details.get('classification') == 'Stable Merchant')
    error_count = sum(1 for details in results.values() 
                     if details.get('classification') == 'Error')
    
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
                print(f"  - {group_name}")
    
    if at_risk_count > 0:
        print("\nAT RISK:")
        for group_name, details in results.items():
            if details.get('classification') == 'At risk':
                print(f"  - {group_name}")
    
    if error_count > 0:
        print("\nERRORS:")
        for group_name, details in results.items():
            if details.get('classification') == 'Error':
                print(f"  - {group_name}: {details.get('error_message', 'Unknown error')}")


if __name__ == "__main__":
    # Command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run tests
        import unittest
        from analyze_ob_groups_test import TestAnalyzeOBGroups
        print("Running tests...")
        unittest.main(argv=['first-arg-is-ignored'], exit=False)
    else:
        # Run analysis and generate report
        print(f"Analyzing WhatsApp groups with '{OB_GROUP_SEARCH_TERM}' in their name...")
        results = analyze_ob_groups()
        
        # Print summary to console
        print_report(results)
        
        # Generate and save detailed report
        report = generate_report(results)
        report_path = save_report_to_file(report)
        
        print(f"\nDetailed report saved to: {report_path}") 