#!/bin/bash

echo "🚀 Pushing Gmail Email Agent to GitHub"
echo "======================================"

# Final security check
echo ""
echo "🔒 Security Check:"
echo "Verifying no sensitive files will be pushed..."

# Check if any sensitive files are tracked
SENSITIVE_FILES=(
    ".env"
    "config/credentials.json"
    "config/token.json"
)

SECURITY_OK=true

for file in "${SENSITIVE_FILES[@]}"; do
    if git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
        echo "❌ SECURITY RISK: $file is tracked by git!"
        SECURITY_OK=false
    else
        echo "✅ $file is safely ignored"
    fi
done

if [ "$SECURITY_OK" = false ]; then
    echo ""
    echo "❌ SECURITY ISSUES DETECTED!"
    echo "Please fix the issues above before pushing to GitHub."
    exit 1
fi

echo ""
echo "✅ Security check passed! No sensitive files will be exposed."

# Check if remote already exists
if git remote get-url origin >/dev/null 2>&1; then
    echo ""
    echo "📡 GitHub remote already configured:"
    echo "   $(git remote get-url origin)"
    
    # Just push
    echo ""
    echo "🚀 Pushing to GitHub..."
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 Successfully pushed to GitHub!"
        echo "🌐 View your repository at: $(git remote get-url origin)"
    else
        echo ""
        echo "❌ Push failed. Please check your GitHub settings and try again."
    fi
    
else
    echo ""
    echo "📡 GitHub remote not configured yet."
    echo ""
    echo "Please provide your GitHub repository URL:"
    echo "Example: https://github.com/scocarter/gmail-email-agent.git"
    read -p "GitHub repo URL: " repo_url
    
    if [ -z "$repo_url" ]; then
        echo "❌ No URL provided. Exiting."
        exit 1
    fi
    
    # Add remote and push
    echo ""
    echo "🔗 Adding GitHub remote..."
    git remote add origin "$repo_url"
    
    echo "🚀 Pushing to GitHub..."
    git branch -M main
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 Successfully created and pushed to GitHub!"
        echo "🌐 View your repository at: $repo_url"
        echo ""
        echo "📋 Next steps:"
        echo "1. ⭐ Star your repository if you like it"
        echo "2. 📝 Update the README with your GitHub username"
        echo "3. 🏷️ Create a release tag when ready"
        echo "4. 📢 Share your project with others!"
    else
        echo ""
        echo "❌ Push failed. Please check your GitHub settings and try again."
        echo "Common issues:"
        echo "- Make sure the repository exists on GitHub"
        echo "- Check your GitHub authentication (SSH keys or HTTPS token)"
        echo "- Verify the repository URL is correct"
    fi
fi
