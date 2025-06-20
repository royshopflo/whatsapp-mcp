#!/usr/bin/env python3
"""
Test file for Slack integration functionality
Tests the requirements before implementing the main Slack sender
"""

import pytest
import os
from unittest.mock import Mock, patch
import requests


class TestSlackIntegration:
    """Test class for Slack integration requirements"""
    
    def test_slack_webhook_url_exists(self):
        """Test that Slack webhook URL is available"""
        # This should be set as environment variable
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        assert webhook_url is not None, "SLACK_WEBHOOK_URL environment variable must be set"
        assert webhook_url.startswith('https://hooks.slack.com/'), "Invalid Slack webhook URL format"
    
    def test_slack_message_format(self):
        """Test that Slack message formatting works correctly"""
        from send_to_slack_group import format_message_for_slack
        
        test_analysis = "📊 **TEST ANALYSIS**\n• Item 1\n• Item 2"
        formatted = format_message_for_slack(test_analysis)
        
        assert isinstance(formatted, dict), "Formatted message should be a dictionary"
        assert 'text' in formatted, "Message should have 'text' field"
        assert 'blocks' in formatted or 'attachments' in formatted, "Message should have rich formatting"
    
    def test_slack_api_connection(self):
        """Test Slack API connection"""
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {'ok': True}
            
            from send_to_slack_group import test_slack_connection
            result = test_slack_connection()
            
            assert result is True, "Slack connection test should pass"
            mock_post.assert_called_once()
    
    def test_slack_message_sending(self):
        """Test sending message to Slack"""
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {'ok': True}
            
            from send_to_slack_group import send_to_slack_with_retry
            result = send_to_slack_with_retry("Test message")
            
            assert result is True, "Message sending should succeed"
    
    def test_slack_error_handling(self):
        """Test error handling for Slack API failures"""
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 400
            mock_post.return_value.json.return_value = {'ok': False, 'error': 'test_error'}
            
            from send_to_slack_group import send_to_slack_with_retry
            result = send_to_slack_with_retry("Test message")
            
            assert result is False, "Message sending should fail gracefully"
    
    def test_dynamic_analysis_integration(self):
        """Test integration with existing dynamic analysis"""
        try:
            from dynamic_analysis import main as generate_dynamic_analysis
            analysis = generate_dynamic_analysis()
            assert isinstance(analysis, str), "Dynamic analysis should return a string"
            assert len(analysis) > 0, "Dynamic analysis should not be empty"
        except ImportError:
            pytest.skip("Dynamic analysis not available")


if __name__ == "__main__":
    print("🧪 Running Slack Integration Tests")
    print("=" * 50)
    
    # Basic environment check
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        print("❌ SLACK_WEBHOOK_URL environment variable not set")
        print("💡 Please set it with: export SLACK_WEBHOOK_URL='your_webhook_url'")
    else:
        print("✅ SLACK_WEBHOOK_URL environment variable found")
    
    print("\n🔍 To run full tests: python -m pytest test_slack_integration.py -v") 