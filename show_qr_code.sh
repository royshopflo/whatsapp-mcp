#!/bin/bash

# Script to show WhatsApp QR code for authentication

echo "🔍 Checking WhatsApp bridge status..."
echo "======================================"

# Check if bridge is running
if pgrep -f "./main" > /dev/null; then
    echo "✅ WhatsApp bridge is running"
    
    # Check if API is responding
    if curl -s http://localhost:8080/ > /dev/null 2>&1; then
        echo "✅ Bridge API is responding"
        echo "✅ Bridge is connected to WhatsApp!"
    else
        echo "⚠️  Bridge API is not responding yet"
        echo "📱 The bridge is waiting for QR code authentication"
        echo ""
        echo "To complete authentication:"
        echo "1. Look for a QR code in the terminal where the bridge is running"
        echo "2. Open WhatsApp on your phone"
        echo "3. Go to Settings > Linked Devices"
        echo "4. Tap 'Link a Device'"
        echo "5. Scan the QR code shown in the terminal"
        echo ""
        echo "If you don't see the QR code, try running:"
        echo "cd whatsapp-bridge && ./main"
        echo ""
        echo "This will show the QR code directly in the terminal"
    fi
else
    echo "❌ WhatsApp bridge is not running"
    echo "Starting bridge..."
    cd whatsapp-bridge && ./main
fi 