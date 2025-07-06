#!/bin/bash

echo "📊 Gmail Email Agent Setup Status"
echo "================================="

# Check virtual environment
if [ -d ".venv" ]; then
    echo "✅ Virtual environment created"
else
    echo "❌ Virtual environment not found"
fi

# Check if we're in virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ Virtual environment activated"
else
    echo "⚠️  Virtual environment not activated (run: source .venv/bin/activate)"
fi

# Check Python packages
echo ""
echo "📦 Python Dependencies:"
if [ -n "$VIRTUAL_ENV" ]; then
    python3 -c "import googleapiclient; print('✅ Gmail API client installed')" 2>/dev/null || echo "❌ Gmail API client missing"
    python3 -c "import google.auth; print('✅ Google Auth installed')" 2>/dev/null || echo "❌ Google Auth missing"
    python3 -c "import yaml; print('✅ PyYAML installed')" 2>/dev/null || echo "❌ PyYAML missing"
else
    echo "⚠️  Activate virtual environment first to check packages"
fi

# Check credentials file
echo ""
echo "🔑 Gmail API Credentials:"
if [ -f "config/credentials.json" ]; then
    echo "✅ Credentials file exists"
    if python3 -c "import json; json.load(open('config/credentials.json'))" 2>/dev/null; then
        echo "✅ Credentials file is valid JSON"
    else
        echo "❌ Credentials file is invalid"
    fi
else
    echo "❌ Credentials file missing"
    
    # Check Downloads folder
    CRED_FILE=$(find ~/Downloads -name "client_secret_*.json" -type f 2>/dev/null | head -1)
    if [ -n "$CRED_FILE" ]; then
        echo "💡 Found credentials file in Downloads: $(basename "$CRED_FILE")"
        echo "   Run: ./setup_gmail_api.sh"
    else
        echo "💡 No credentials file found. Please:"
        echo "   1. Go to https://console.cloud.google.com/apis/credentials"
        echo "   2. Create OAuth client ID (Desktop application)"
        echo "   3. Download the JSON file"
        echo "   4. Run: ./setup_gmail_api.sh"
    fi
fi

# Check configuration
echo ""
echo "⚙️  Configuration:"
if [ -f "config/config.yaml" ]; then
    echo "✅ Configuration file exists"
else
    echo "❌ Configuration file missing"
fi

# Next steps
echo ""
echo "📋 Next Steps:"
if [ ! -f "config/credentials.json" ]; then
    echo "1. ⚡ Complete Google Cloud Console setup and download credentials"
    echo "2. 🔧 Run: ./setup_gmail_api.sh"
    echo "3. 🧪 Run: source .venv/bin/activate && python src/cli.py test"
elif [ ! -f "config/token.json" ]; then
    echo "1. 🧪 Run: source .venv/bin/activate && python src/cli.py test"
    echo "2. 🚀 Run: source .venv/bin/activate && python src/cli.py listen"
else
    echo "1. 🚀 Everything looks ready! Try: source .venv/bin/activate && python src/cli.py listen"
fi

echo ""
echo "🆘 Need help? Check README.txt for detailed instructions"
