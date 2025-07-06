#!/bin/bash

echo "🔑 OpenAI API Key Setup"
echo "======================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
fi

echo ""
echo "Please follow these steps to get your OpenAI API key:"
echo "1. Go to: https://platform.openai.com/api-keys"
echo "2. Sign in to your OpenAI account"
echo "3. Click 'Create new secret key'"
echo "4. Name it 'Gmail Email Agent'"
echo "5. Copy the key (starts with sk-...)"
echo ""

# Prompt for API key
read -p "Enter your OpenAI API key: " api_key

if [ -z "$api_key" ]; then
    echo "❌ No API key provided. Exiting."
    exit 1
fi

# Validate key format (basic check)
if [[ $api_key == sk-* ]]; then
    # Update .env file
    if grep -q "OPENAI_API_KEY=" .env; then
        # Replace existing key
        sed -i '' "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=$api_key/" .env
    else
        # Add new key
        echo "OPENAI_API_KEY=$api_key" >> .env
    fi
    
    echo "✅ OpenAI API key saved to .env file"
    echo ""
    
    # Also export for current session
    export OPENAI_API_KEY="$api_key"
    echo "✅ API key exported for current session"
    echo ""
    
    # Test the key
    echo "🧪 Testing API key..."
    if command -v python3 &> /dev/null; then
        python3 -c "
import os
try:
    import openai
    client = openai.OpenAI(api_key='$api_key')
    # Test with a simple request
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': 'Hello'}],
        max_tokens=5
    )
    print('✅ OpenAI API key is working!')
except ImportError:
    print('⚠️  OpenAI package not installed. Key saved but not tested.')
    print('   Install with: pip install openai')
except Exception as e:
    print(f'❌ API key test failed: {e}')
"
    else
        echo "⚠️  Python not found. API key saved but not tested."
    fi
    
    echo ""
    echo "🎉 OpenAI setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Activate virtual environment: source .venv/bin/activate"
    echo "2. Install OpenAI package: pip install openai"
    echo "3. Test email agent: python src/cli.py test"
    
else
    echo "❌ Invalid API key format. OpenAI keys start with 'sk-'"
    exit 1
fi
