#!/bin/bash

# Complete WhatsApp Authentication Script

echo "🔗 Complete WhatsApp Bridge Authentication"
echo "=========================================="

# Check if bridge is running
if pgrep -f "./main" > /dev/null; then
    echo "✅ Bridge is running"
    
    # Check if API is responding
    if curl -s http://localhost:8081/ > /dev/null 2>&1; then
        echo "✅ Bridge API is responding"
        echo "✅ Bridge is connected to WhatsApp!"
        echo ""
        echo "🎉 Authentication completed successfully!"
        echo "Your cron jobs should now work properly."
    else
        echo "⚠️  Bridge API is not responding yet"
        echo "📱 The bridge is waiting for authentication"
        echo ""
        echo "🔧 To complete authentication:"
        echo ""
        echo "Option 1 - QR Code (Recommended):"
        echo "1. Run: cd whatsapp-bridge && ./main"
        echo "2. Look for the QR code in the terminal"
        echo "3. Open WhatsApp on your phone"
        echo "4. Go to Settings > Linked Devices"
        echo "5. Tap 'Link a Device'"
        echo "6. Scan the QR code"
        echo ""
        echo "Option 2 - Phone Pairing:"
        echo "1. Run: cd whatsapp-bridge && ./main --phone YOUR_PHONE_NUMBER"
        echo "2. Enter your phone number when prompted"
        echo "3. Follow the pairing instructions"
        echo ""
        echo "After authentication, the API will start responding on port 8081"
    fi
else
    echo "❌ Bridge is not running"
    echo "Starting bridge..."
    cd whatsapp-bridge && ./main
fi

echo ""
echo "📋 Test Commands:"
echo "• Test connection: curl -s http://localhost:8081/"
echo "• Test sending: curl -X POST http://localhost:8081/api/send -H 'Content-Type: application/json' -d '{\"recipient\":\"test@test.com\",\"message\":\"test\"}'"
echo "• Check logs: tail -f logs/whatsapp_bridge.log" 