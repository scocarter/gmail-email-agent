#!/bin/bash

echo "🚀 Gmail Email Agent - Project Status"
echo "===================================="

# Git status
echo ""
echo "📂 Git Repository:"
if [ -d ".git" ]; then
    echo "✅ Git repository initialized"
    
    # Check if we have commits
    if git rev-parse HEAD >/dev/null 2>&1; then
        echo "✅ Files committed to git"
        echo "   Latest commit: $(git log -1 --pretty=format:'%h - %s')"
        
        # Check if remote exists
        if git remote get-url origin >/dev/null 2>&1; then
            echo "✅ GitHub remote configured"
            echo "   Remote URL: $(git remote get-url origin)"
        else
            echo "⚠️  GitHub remote not configured"
            echo "   Next: Add remote and push to GitHub"
        fi
    else
        echo "⚠️  No commits yet"
    fi
else
    echo "❌ Git repository not initialized"
fi

# Python environment
echo ""
echo "🐍 Python Environment:"
if [ -d ".venv" ]; then
    echo "✅ Virtual environment created"
    
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "✅ Virtual environment activated"
        
        # Check key packages
        python3 -c "import googleapiclient; print('✅ Gmail API package installed')" 2>/dev/null || echo "❌ Gmail API package missing"
        python3 -c "import openai; print('✅ OpenAI package installed')" 2>/dev/null || echo "❌ OpenAI package missing"
        python3 -c "import yaml; print('✅ PyYAML package installed')" 2>/dev/null || echo "❌ PyYAML package missing"
    else
        echo "⚠️  Virtual environment not activated"
        echo "   Run: source .venv/bin/activate"
    fi
else
    echo "❌ Virtual environment not found"
fi

# Gmail API setup
echo ""
echo "📧 Gmail API Setup:"
if [ -f "config/credentials.json" ]; then
    echo "✅ Gmail credentials configured"
    
    if [ -f "config/token.json" ]; then
        echo "✅ OAuth authentication completed"
    else
        echo "⚠️  OAuth authentication pending"
        echo "   Run: python authenticate.py"
    fi
else
    echo "❌ Gmail credentials missing"
    echo "   Run: ./setup_gmail_api.sh"
fi

# OpenAI API setup
echo ""
echo "🤖 OpenAI API Setup:"
if [ -f ".env" ]; then
    if grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
        echo "✅ OpenAI API key configured in .env"
        
        if [ -n "$OPENAI_API_KEY" ]; then
            echo "✅ OpenAI API key exported"
        else
            echo "⚠️  OpenAI API key not exported for current session"
            echo "   Run: source .env or export OPENAI_API_KEY"
        fi
    else
        echo "⚠️  OpenAI API key not configured"
        echo "   Run: ./setup_openai.sh"
    fi
else
    echo "❌ .env file missing"
    echo "   Run: ./setup_openai.sh"
fi

# Project files
echo ""
echo "📁 Project Files:"
key_files=(
    "src/email_agent.py"
    "src/ai_classifier.py"
    "src/cli.py"
    "config/config.yaml"
    "README.md"
    "requirements-minimal.txt"
)

for file in "${key_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file missing"
    fi
done

# Overall status
echo ""
echo "📊 Overall Status:"

# Count checks
checks_passed=0
total_checks=0

# Git check
total_checks=$((total_checks + 1))
[ -d ".git" ] && git rev-parse HEAD >/dev/null 2>&1 && checks_passed=$((checks_passed + 1))

# Python environment check
total_checks=$((total_checks + 1))
[ -d ".venv" ] && [ -n "$VIRTUAL_ENV" ] && checks_passed=$((checks_passed + 1))

# Gmail API check
total_checks=$((total_checks + 1))
[ -f "config/credentials.json" ] && checks_passed=$((checks_passed + 1))

# OpenAI API check
total_checks=$((total_checks + 1))
[ -f ".env" ] && grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null && checks_passed=$((checks_passed + 1))

echo "Status: $checks_passed/$total_checks core components ready"

if [ $checks_passed -eq $total_checks ]; then
    echo "🎉 Project is fully set up and ready to use!"
    echo ""
    echo "🚀 Quick Start Commands:"
    echo "  source .venv/bin/activate     # Activate environment"
    echo "  python authenticate.py        # Complete Gmail auth (if needed)"
    echo "  python src/cli.py test        # Test the system"
    echo "  python src/cli.py listen      # Start monitoring emails"
else
    echo "⚠️  Setup incomplete. Please address the items above."
fi

echo ""
echo "📚 Documentation:"
echo "  README.md          # GitHub documentation"
echo "  README.txt         # Detailed setup guide"
echo ""
echo "🔧 Setup Scripts:"
echo "  ./setup_gmail_api.sh    # Gmail API credentials"
echo "  ./setup_openai.sh       # OpenAI API key"
echo "  ./authenticate.py       # Gmail OAuth"
echo "  ./check_status.sh       # Quick status check"
echo ""
echo "💡 Need help? Check the documentation or run individual setup scripts."
