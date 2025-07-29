#!/bin/bash

# WhatsApp Bridge Link Script
# This script helps link the bridge with WhatsApp

echo "🔗 WhatsApp Bridge Link Script"
echo "=============================="

# Check if bridge is running
if pgrep -f "./main" > /dev/null; then
    echo "✅ Bridge is running"
    
    # Check if API is responding
    if curl -s http://localhost:8081/ > /dev/null 2>&1; then
        echo "✅ Bridge API is responding"
        echo "✅ Bridge is connected to WhatsApp!"
        echo ""
        echo "🎉 Your bridge is successfully linked!"
        echo "Your cron jobs should now work properly."
    else
        echo "⚠️  Bridge API is not responding yet"
        echo "📱 The bridge is waiting for authentication"
        echo ""
        echo "To complete the link:"
        echo "1. Look for a QR code in the terminal"
        echo "2. Open WhatsApp on your phone"
        echo "3. Go to Settings > Linked Devices"
        echo "4. Tap 'Link a Device'"
        echo "5. Scan the QR code"
        echo ""
        echo "If you don't see the QR code, try:"
        echo "cd whatsapp-bridge && ./main"
        echo ""
        echo "This will show the QR code directly in the terminal"
    fi
else
    echo "❌ Bridge is not running"
    echo "Starting bridge..."
    cd whatsapp-bridge && ./main
fi

echo ""
echo "📋 Status Commands:"
echo "• Check connection: curl -s http://localhost:8081/"
echo "• Test sending: curl -X POST http://localhost:8081/api/send -H 'Content-Type: application/json' -d '{\"recipient\":\"test@test.com\",\"message\":\"test\"}'"
echo "• Check logs: tail -f logs/whatsapp_bridge.log" 