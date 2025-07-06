# 🔐 Security Guidelines

## Protected Files

The following sensitive files are automatically excluded from version control:

### API Keys & Credentials
- `.env` - Environment variables including OpenAI API key
- `config/credentials.json` - Google OAuth client credentials
- `config/token.json` - Google OAuth access tokens

### Generated Data
- `data/` - SQLite database files
- `logs/` - Application log files
- `backups/` - Database backup files

## Security Best Practices

### 🔑 API Key Management
1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate keys regularly** and revoke unused keys
4. **Monitor usage** through provider dashboards

### 📧 Email Data Privacy
1. **Local storage only** - no cloud synchronization
2. **Encrypted credentials** using OAuth2 tokens
3. **Automatic token refresh** for security
4. **Rate limiting** to prevent abuse

### 🛡️ System Security
1. **Virtual environment isolation** for dependencies
2. **Input validation** for all external data
3. **Error handling** without exposing sensitive information
4. **Logging controls** to avoid logging secrets

## Setup Security Checklist

- [ ] ✅ `.gitignore` properly configured
- [ ] ✅ API keys stored in `.env` file only
- [ ] ✅ OAuth credentials in `config/credentials.json` (ignored)
- [ ] ✅ No hardcoded secrets in source code
- [ ] ✅ Virtual environment activated for dependencies
- [ ] ✅ Rate limiting configured for API requests

## Emergency Procedures

### If API Key is Compromised
1. **Immediately revoke** the key at the provider
2. **Generate a new key** and update `.env`
3. **Review recent usage** for unauthorized access
4. **Update security practices** if needed

### If OAuth Token is Compromised
1. **Delete** `config/token.json`
2. **Re-run authentication** with `python authenticate.py`
3. **Review Gmail account** for unauthorized access
4. **Consider revoking app access** in Google Account settings

## Reporting Security Issues

If you discover a security vulnerability, please:
1. **DO NOT** create a public GitHub issue
2. **Contact** the project maintainer directly
3. **Provide** detailed information about the vulnerability
4. **Allow time** for the issue to be addressed before disclosure

---

**Remember**: Security is everyone's responsibility. When in doubt, err on the side of caution.
