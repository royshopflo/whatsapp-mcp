import unittest
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Mock class for testing
class MockMessage:
    def __init__(self, timestamp, sender, content, is_from_me, chat_jid="test_chat@g.us", id="test_id"):
        self.timestamp = timestamp
        self.sender = sender
        self.content = content
        self.is_from_me = is_from_me
        self.chat_jid = chat_jid
        self.id = id

class MockChat:
    def __init__(self, jid, name, last_message_time=None, last_message=None, last_sender=None, last_is_from_me=None):
        self.jid = jid
        self.name = name
        self.last_message_time = last_message_time
        self.last_message = last_message
        self.last_sender = last_sender 
        self.last_is_from_me = last_is_from_me

    @property
    def is_group(self) -> bool:
        """Determine if chat is a group based on JID pattern."""
        return self.jid.endswith("@g.us")

class TestAnalyzeOBGroups(unittest.TestCase):
    """Tests for analyzing OB groups and classifying merchants"""
    
    def test_find_ob_groups(self):
        """Test finding groups with (OB) in their name"""
        mock_chats = [
            MockChat('123@g.us', 'Test Group (OB)'),
            MockChat('456@g.us', 'Another (OB) Group'),
            MockChat('789@g.us', 'Regular Group'),
            MockChat('101@s.whatsapp.net', 'Individual Chat')
        ]
        
        # Mock the list_chats function to return our mock data
        original_list_chats = None
        try:
            # Import the module
            import whatsapp
            original_list_chats = whatsapp.list_chats
            
            # Replace with our mock
            def mock_list_chats(*args, **kwargs):
                return mock_chats
            
            # Apply monkey patch
            whatsapp.list_chats = mock_list_chats
            
            # Now import and run our function
            from analyze_ob_groups_5days import find_ob_groups
            ob_groups = find_ob_groups()
            
            # Assertions
            self.assertEqual(len(ob_groups), 2, "Should find exactly 2 OB groups")
            self.assertTrue(all("(OB)" in g.name for g in ob_groups), "All groups should have (OB) in name")
            self.assertTrue(all(g.jid.endswith("@g.us") for g in ob_groups), "All should be group JIDs")
            
        finally:
            # Restore original function if it existed
            if original_list_chats:
                whatsapp.list_chats = original_list_chats
    
    def test_needs_attention_classification(self):
        """Test that messages with negative sentiment are classified as Needs Attention"""
        now = datetime.now()
        
        # Messages with negative sentiment
        negative_messages = [
            MockMessage(now - timedelta(days=1), "user1", "I'm very annoyed with the service", False),
            MockMessage(now - timedelta(days=1, hours=1), "user2", "Response looking good", False)
        ]
        
        # To be imported from implementation
        from analyze_ob_groups_5days import analyze_sentiment
        
        result = analyze_sentiment(negative_messages, [])
        self.assertEqual(result, "Needs attention", "Messages with negative sentiment should be classified as 'Needs attention'")
    
    def test_at_risk_classification(self):
        """Test that delayed responses are classified as At Risk"""
        now = datetime.now()
        shopflo_team = ["team1", "team2"]
        
        # Messages with delayed response (merchant message, then Shopflo response after 2+ hours)
        delayed_response_messages = [
            MockMessage(now - timedelta(days=2), "merchant1", "Hello, need some help", False),
            # Response comes after more than 2 hours
            MockMessage(now - timedelta(days=2) + timedelta(hours=3), "team1", "Sorry for the delay, how can I help?", True)
        ]
        
        from analyze_ob_groups_5days import analyze_sentiment
        
        result = analyze_sentiment(delayed_response_messages, shopflo_team)
        self.assertEqual(result, "At risk", "Delayed responses should be classified as 'At risk'")
    
    def test_stable_merchant_classification(self):
        """Test that normal conversations are classified as Stable Merchant"""
        now = datetime.now()
        shopflo_team = ["team1", "team2"]
        
        # Normal conversations - timely responses, no negative sentiment
        normal_messages = [
            MockMessage(now - timedelta(days=3), "merchant2", "Good morning, quick question", False),
            MockMessage(now - timedelta(days=3) + timedelta(minutes=30), "team1", "Good morning! How can I help?", True),
            MockMessage(now - timedelta(days=1), "merchant2", "Thanks for your help!", False)
        ]
        
        from analyze_ob_groups_5days import analyze_sentiment
        
        result = analyze_sentiment(normal_messages, shopflo_team)
        self.assertEqual(result, "Stable Merchant", "Normal conversations should be classified as 'Stable Merchant'")


if __name__ == "__main__":
    unittest.main() 