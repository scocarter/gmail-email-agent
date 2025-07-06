#!/bin/bash

# Gmail API Setup Helper Script
echo "🔧 Gmail API Setup Helper"
echo "========================="

# Check if credentials file exists in Downloads
DOWNLOADS_DIR="$HOME/Downloads"
CREDENTIALS_FILE=$(find "$DOWNLOADS_DIR" -name "client_secret_*.json" -type f | head -1)

if [ -z "$CREDENTIALS_FILE" ]; then
    echo "❌ No client_secret_*.json file found in ~/Downloads"
    echo ""
    echo "Please follow these steps:"
    echo "1. Go to https://console.cloud.google.com/apis/credentials"
    echo "2. Click 'CREATE CREDENTIALS' → 'OAuth client ID'"
    echo "3. Choose 'Desktop application'"
    echo "4. Download the JSON file"
    echo "5. Run this script again"
    echo ""
    exit 1
fi

echo "✅ Found credentials file: $(basename "$CREDENTIALS_FILE")"

# Create config directory if it doesn't exist
mkdir -p config

# Copy and rename the file
cp "$CREDENTIALS_FILE" "config/credentials.json"

if [ $? -eq 0 ]; then
    echo "✅ Credentials file copied to config/credentials.json"
    
    # Verify the file structure
    if python3 -c "import json; json.load(open('config/credentials.json'))" 2>/dev/null; then
        echo "✅ Credentials file is valid JSON"
        
        # Show the client info (without sensitive data)
        echo ""
        echo "📋 Client Information:"
        python3 -c "
import json
with open('config/credentials.json') as f:
    data = json.load(f)
    client_info = data.get('installed', {})
    print(f'Client ID: {client_info.get(\"client_id\", \"Unknown\")[:20]}...')
    print(f'Project ID: {client_info.get(\"project_id\", \"Unknown\")}')
"
        
        echo ""
        echo "🎉 Gmail API setup complete!"
        echo ""
        echo "Next steps:"
        echo "1. Run: python src/cli.py test"
        echo "2. This will open a browser for Gmail authentication"
        echo "3. Grant permissions to your application"
        echo ""
        
        # Clean up the downloaded file
        echo "🧹 Cleaning up downloaded file..."
        rm "$CREDENTIALS_FILE"
        echo "✅ Removed original file from Downloads"
        
    else
        echo "❌ Invalid JSON file format"
        exit 1
    fi
else
    echo "❌ Failed to copy credentials file"
    exit 1
fi
