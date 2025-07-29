#!/bin/bash

# Test WhatsApp Bridge Connection

echo "🔍 Testing WhatsApp Bridge Connection"
echo "====================================="

# Check if bridge process is running
if pgrep -f "./main" > /dev/null; then
    echo "✅ Bridge process is running"
    
    # Check if API is responding
    if curl -s http://localhost:8081/ > /dev/null 2>&1; then
        echo "✅ Bridge API is responding"
        
        # Test sending a message
        echo "🧪 Testing message sending..."
        response=$(curl -s -X POST http://localhost:8081/api/send \
            -H "Content-Type: application/json" \
            -d '{"recipient":"test@test.com","message":"Connection test"}' 2>/dev/null || echo '{"success":false,"message":"API not responding"}')
        
        echo "📤 Response: $response"
        
        if echo "$response" | grep -q '"success":true'; then
            echo "✅ Bridge is connected to WhatsApp!"
            echo "✅ Your cron jobs should work now!"
        elif echo "$response" | grep -q "Not connected to WhatsApp"; then
            echo "❌ Bridge is not connected to WhatsApp"
            echo "🔧 Run './fix_whatsapp_bridge.sh' to fix this"
        else
            echo "⚠️  Bridge status unclear"
            echo "🔧 Run './fix_whatsapp_bridge.sh' to fix this"
        fi
    else
        echo "❌ Bridge API is not responding"
        echo "🔧 Run './fix_whatsapp_bridge.sh' to fix this"
    fi
else
    echo "❌ Bridge process is not running"
    echo "🔧 Run './fix_whatsapp_bridge.sh' to start the bridge"
fi

echo ""
echo "📋 Quick Commands:"
echo "• Test connection: ./test_bridge_connection.sh"
echo "• Fix bridge: ./fix_whatsapp_bridge.sh"
echo "• Check logs: tail -f logs/whatsapp_bridge.log" 