import unittest
from typing import List, Dict, Any, Union
from datetime import datetime, timedelta
import re
from whatsapp import (
    list_chats, 
    list_messages, 
    classify_group_messages, 
    Message,
    Chat
)

# Constants
OB_GROUP_SEARCH_TERM = "(OB)"
DAYS_TO_ANALYZE = 5
SHOPFLO_TEAM_NUMBERS = [
    # Add Shopflo team phone numbers here in the format "123456789"
    # These should be the phone numbers of the Shopflo team members
]

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

# Function to test for valid date string format
def is_valid_date_format(date_str: str) -> bool:
    try:
        datetime.fromisoformat(date_str)
        return True
    except ValueError:
        return False


def analyze_sentiment(messages: List[Union[Message, str]]) -> str:
    """
    Analyze the sentiment of messages to categorize the group
    
    Args:
        messages: List of Message objects or strings
        
    Returns:
        One of: "Needs attention", "At risk", or "Stable Merchant"
    """
    # 1. Check for negative sentiment keywords
    for msg in messages:
        content = msg.content if isinstance(msg, Message) else str(msg)
        for keyword in NEGATIVE_KEYWORDS:
            if re.search(keyword, content, re.IGNORECASE):
                print(f"Found negative sentiment: '{keyword}' in message: '{content[:100]}...'")
                return "Needs attention"
    
    # 2. Check for delayed responses
    # - For string messages, we can't really do this without timestamps
    # - For Message objects, this would require identifying which are from merchants vs. Shopflo
    
    # Since we can't do time-based analysis on the current data, classify as stable
    return "Stable Merchant"


class TestAnalyzeOBGroups(unittest.TestCase):
    """Test cases for analyzing OB groups"""
    
    def test_identify_ob_groups(self):
        """Test that we can identify groups with (OB) in their name"""
        # Mock the list_chats function for testing
        global list_chats
        original_list_chats = list_chats
        
        def mock_list_chats(*args, **kwargs):
            return [
                {'jid': '123@g.us', 'name': 'Test Group (OB)'},
                {'jid': '456@g.us', 'name': 'Another (OB) Group'},
                {'jid': '789@s.whatsapp.net', 'name': 'Not a group'},
                {'jid': '321@g.us', 'name': 'Group without OB'}
            ]
        
        try:
            list_chats = mock_list_chats
            groups = find_ob_groups()
            
            # There should be at least one group returned
            self.assertTrue(len(groups) > 0, "No OB groups found")
            
            # Every group should contain (OB) in its name
            for group in groups:
                self.assertIn(OB_GROUP_SEARCH_TERM, group.get('name', ''), 
                              f"Group {group.get('name')} doesn't contain {OB_GROUP_SEARCH_TERM}")
        finally:
            # Restore the original function
            list_chats = original_list_chats
    
    def test_get_recent_messages(self):
        """Test that we can get messages from the last 5 days"""
        # Mock the list_messages function for testing
        global list_messages
        original_list_messages = list_messages
        
        now = datetime.now()
        
        def mock_list_messages(*args, **kwargs):
            return [
                Message(
                    timestamp=now - timedelta(days=1),
                    sender="1234",
                    content="Test message 1",
                    is_from_me=False,
                    chat_jid="1234@g.us",
                    id="msg1"
                ),
                Message(
                    timestamp=now - timedelta(days=3),
                    sender="5678",
                    content="Test message 2",
                    is_from_me=True,
                    chat_jid="1234@g.us",
                    id="msg2"
                )
            ]
        
        try:
            list_messages = mock_list_messages
            
            # Create a mock group with a JID
            mock_group = {'jid': '1234@g.us', 'name': 'Test (OB) Group'}
            
            # Get recent messages
            messages = get_recent_messages(mock_group['jid'])
            
            # Check that all messages are within the last 5 days
            cutoff_date = (datetime.now() - timedelta(days=DAYS_TO_ANALYZE))
            
            for msg in messages:
                self.assertGreaterEqual(msg.timestamp, cutoff_date, 
                                f"Message with timestamp {msg.timestamp} is older than {DAYS_TO_ANALYZE} days")
        finally:
            # Restore the original function
            list_messages = original_list_messages
    
    def test_sentiment_analysis(self):
        """Test the sentiment analysis function"""
        # Test case 1: Negative sentiment
        msgs1 = [
            Message(
                timestamp=datetime.now(),
                sender="3333",
                content="I am very disappointed with Shopflo",
                is_from_me=False,
                chat_jid="1234@g.us",
                id="1"
            )
        ]
        
        classification1 = analyze_sentiment(msgs1)
        self.assertEqual("Needs attention", classification1, "Failed to classify as 'Needs attention'")
        
        # Test case 2: String messages with negative sentiment
        msgs2 = [
            "Very frustrated with the delays in response",
            "Everything is working well"
        ]
        
        classification2 = analyze_sentiment(msgs2)
        self.assertEqual("Needs attention", classification2, "Failed to classify string messages as 'Needs attention'")
        
        # Test case 3: Stable sentiment
        msgs3 = [
            Message(
                timestamp=datetime.now(),
                sender="5555",
                content="Thank you for your help!",
                is_from_me=False,
                chat_jid="1234@g.us",
                id="3"
            ),
            Message(
                timestamp=datetime.now(),
                sender="1111",
                content="You're welcome!",
                is_from_me=True,
                chat_jid="1234@g.us",
                id="4"
            )
        ]
        
        classification3 = analyze_sentiment(msgs3)
        self.assertEqual("Stable Merchant", classification3, "Failed to classify as 'Stable Merchant'")


def find_ob_groups() -> List[Dict[str, Any]]:
    """
    Find all WhatsApp groups with (OB) in their name
    
    Returns:
        List of group dictionaries with jid, name, and other metadata
    """
    # List all chats
    chats = list_chats(limit=100)
    
    # Convert Chat objects to dictionaries if needed
    chat_dicts = []
    for chat in chats:
        if isinstance(chat, Chat):
            chat_dict = {
                'jid': chat.jid,
                'name': chat.name,
                'last_message_time': chat.last_message_time,
                'last_message': chat.last_message,
                'last_sender': chat.last_sender,
                'last_is_from_me': chat.last_is_from_me
            }
            chat_dicts.append(chat_dict)
        elif isinstance(chat, dict):
            chat_dicts.append(chat)
    
    # Filter to only include groups with (OB) in their name
    ob_groups = [chat for chat in chat_dicts if 
                OB_GROUP_SEARCH_TERM in chat.get('name', '') and
                chat.get('jid', '').endswith('@g.us')]
    
    return ob_groups


def get_recent_messages(chat_jid: str, message_limit: int = 200) -> List[Union[Message, str]]:
    """
    Get messages from the specified chat from the last DAYS_TO_ANALYZE days
    
    Args:
        chat_jid: The JID of the chat to get messages from
        message_limit: Maximum number of messages to retrieve
        
    Returns:
        List of Message objects or strings
    """
    # Calculate date cutoff
    after_date = (datetime.now() - timedelta(days=DAYS_TO_ANALYZE)).isoformat()
    
    # Get messages
    raw_messages = list_messages(
        after=after_date,
        chat_jid=chat_jid,
        limit=message_limit  # Increased to get more messages for analysis
    )
    
    # Print sample messages for inspection
    if len(raw_messages) > 0:
        first_msg = raw_messages[0]
        print(f"Sample message type: {type(first_msg)}")
        
        # Print the first 3 messages (or fewer if there aren't that many)
        sample_count = min(3, len(raw_messages))
        for i in range(sample_count):
            # Truncate messages to 200 chars for readability
            if isinstance(raw_messages[i], str):
                msg_str = raw_messages[i]
                print(f"Message {i+1}: {msg_str[:200]}...")
            else:
                # If it's a Message object, print its content attribute
                try:
                    content = getattr(raw_messages[i], 'content', str(raw_messages[i]))
                    print(f"Message {i+1}: {content[:200]}...")
                except:
                    print(f"Message {i+1}: {str(raw_messages[i])[:200]}...")
    
    return raw_messages


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
            print(f"Found {len(messages)} messages in the last {DAYS_TO_ANALYZE} days")
            
            # Classify the group based on sentiment analysis
            classification = analyze_sentiment(messages)
            
            # Store results
            results[group_name] = {
                'classification': classification,
                'message_count': len(messages),
                'jid': group_jid
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
    # Run tests if in test mode
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        unittest.main(argv=['first-arg-is-ignored'])
    else:
        # Run actual analysis
        results = analyze_ob_groups()
        print_report(results) 