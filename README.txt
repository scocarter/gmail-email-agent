# Gmail Email Agent

## Description
The Gmail Email Agent is an intelligent Python-based service that automatically manages your Gmail inbox using AI-driven email classification. It categorizes emails into Important, Promotional, Social, and Junk categories, then takes appropriate actions like moving emails to specific folders or sending notifications for important messages.

### Key Features
- **AI-Powered Classification**: Uses OpenAI GPT or rule-based classification
- **Real-time Processing**: Listens for new emails and processes them automatically
- **Batch Processing**: Scan and reclassify past emails within specified timeframes
- **Junk Detection**: Identify potential spam/junk emails with user confirmation before deletion
- **Smart Notifications**: Desktop notifications for important emails on macOS
- **Database Tracking**: SQLite database for tracking classifications and statistics
- **Three Operating Modes**:
  1. **Listener Mode**: Continuously monitors for new emails
  2. **Batch Processor Mode**: Processes historical emails
  3. **Junk Detector Mode**: Finds and manages junk emails

## Prerequisites

- **Python 3.8+** (recommended: 3.9 or higher)
- **macOS** (for notification features)
- **Gmail Account** with API access
- **OpenAI API Key** (optional, for AI classification)

## Detailed Setup Instructions

### Step 1: Install Python Dependencies

1. **Navigate to the project directory:**
   ```bash
   cd /Users/scocarter/projects/gmail-email-agent
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   ```

3. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Gmail API Setup

1. **Create a Google Cloud Project:**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Gmail API:
     - Navigate to "APIs & Services" > "Library"
     - Search for "Gmail API" and click "Enable"

2. **Create Credentials:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop application"
   - Download the credentials JSON file
   - Rename it to `credentials.json` and place it in the `config/` directory

3. **Set up OAuth Consent Screen:**
   - Go to "APIs & Services" > "OAuth consent screen"
   - Fill in the required information
   - Add your Gmail address to test users

### Step 3: OpenAI API Setup (Optional)

1. **Get OpenAI API Key:**
   - Sign up at [OpenAI](https://platform.openai.com/)
   - Navigate to API Keys and create a new key

2. **Set Environment Variable:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   
   Or add to your shell profile (`~/.bashrc`, `~/.zshrc`):
   ```bash
   echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.zshrc
   source ~/.zshrc
   ```

### Step 4: Configuration

1. **Review and customize `config/config.yaml`:**
   - Adjust AI settings (provider, model, confidence thresholds)
   - Configure email processing parameters
   - Set notification preferences
   - Customize classification keywords

2. **Important settings to review:**
   ```yaml
   ai:
     provider: "openai"  # or "local" for rule-based
     model: "gpt-4-turbo-preview"
   
   notifications:
     enabled: true
     important_emails:
       popup: true
       sound: true
   
   classification:
     categories:
       important:
         keywords: ["urgent", "deadline", "meeting"]
         senders: ["boss@company.com"]
   ```

## Running the Application

### Command Line Interface

The application provides a comprehensive CLI. Use the following commands:

1. **Test the setup:**
   ```bash
   python src/cli.py test
   ```

2. **Start listener mode (continuous monitoring):**
   ```bash
   python src/cli.py listen
   ```

3. **Process past emails (batch mode):**
   ```bash
   python src/cli.py batch --timeframe 7d
   ```
   
   Timeframe options: `7d` (7 days), `2w` (2 weeks), `1m` (1 month)

4. **Detect and review junk emails:**
   ```bash
   python src/cli.py junk
   ```

5. **View statistics:**
   ```bash
   python src/cli.py stats
   ```

6. **Create database backup:**
   ```bash
   python src/cli.py backup
   ```

7. **Clean old data:**
   ```bash
   python src/cli.py cleanup --days 90
   ```

### First Run Authentication

On the first run, the application will:
1. Open your web browser
2. Ask you to sign in to your Google account
3. Request permission to access your Gmail
4. Save authentication tokens locally for future use

### Running as a Background Service

To run the agent continuously in the background:

1. **Using screen (recommended for testing):**
   ```bash
   screen -S gmail-agent
   python src/cli.py listen
   # Press Ctrl+A, then D to detach
   # Use "screen -r gmail-agent" to reattach
   ```

2. **Using nohup:**
   ```bash
   nohup python src/cli.py listen > logs/agent.out 2>&1 &
   ```

3. **Create a launchd service (macOS):**
   Create `~/Library/LaunchAgents/com.user.gmail-agent.plist`:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.user.gmail-agent</string>
       <key>ProgramArguments</key>
       <array>
           <string>/path/to/python</string>
           <string>/Users/scocarter/projects/gmail-email-agent/src/cli.py</string>
           <string>listen</string>
       </array>
       <key>RunAtLoad</key>
       <true/>
       <key>KeepAlive</key>
       <true/>
   </dict>
   </plist>
   ```
   
   Then load it:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.user.gmail-agent.plist
   ```

## Configuration Details

### Email Classification Categories

- **Important**: Work emails, deadlines, meetings, financial matters
- **Promotional**: Marketing emails, newsletters, sales offers
- **Social**: Social media notifications, friend requests
- **Junk**: Spam, phishing attempts, suspicious emails

### AI Classification

The system supports two modes:

1. **OpenAI Mode** (recommended):
   - Uses GPT models for intelligent classification
   - Requires OPENAI_API_KEY environment variable
   - More accurate but costs money per request

2. **Rule-based Mode**:
   - Uses keyword matching and heuristics
   - Free but less accurate
   - Automatically used if OpenAI is not configured

### Notification System

- **Desktop Notifications**: Uses macOS notification system
- **Sound Alerts**: Plays system sounds for important emails
- **System Tray**: Shows agent status and statistics

## File Structure

```
gmail-email-agent/
├── config/
│   ├── config.yaml              # Main configuration
│   └── credentials.json         # Gmail API credentials
├── src/
│   ├── email_agent.py          # Main agent class
│   ├── ai_classifier.py        # AI classification logic
│   ├── email_processor.py      # Email parsing and processing
│   ├── notification_manager.py # System notifications
│   ├── database_manager.py     # SQLite database operations
│   ├── utils.py               # Utility functions
│   └── cli.py                 # Command-line interface
├── data/                      # Database and cached data
├── logs/                      # Log files
├── tests/                     # Unit tests
├── requirements.txt           # Python dependencies
└── README.txt                # This file
```

## Troubleshooting

### Common Issues

1. **"credentials.json not found"**
   - Ensure you've downloaded the OAuth credentials from Google Cloud Console
   - Place the file in the `config/` directory
   - Make sure it's named exactly `credentials.json`

2. **"OPENAI_API_KEY not set"**
   - Set the environment variable: `export OPENAI_API_KEY="your-key"`
   - Or configure the system to use rule-based classification in `config.yaml`

3. **"Permission denied" errors**
   - Re-run the OAuth flow: delete `config/token.json` and restart
   - Check that your Gmail account has the necessary permissions

4. **No notifications appearing**
   - Check macOS notification settings for the Terminal app
   - Ensure notification permissions are enabled

5. **Database errors**
   - Check that the `data/` directory is writable
   - Try running: `python src/cli.py test`

### Debugging

1. **Enable debug logging:**
   Edit `config/config.yaml`:
   ```yaml
   logging:
     level: "DEBUG"
   ```

2. **Check log files:**
   ```bash
   tail -f logs/email_agent.log
   ```

3. **Test individual components:**
   ```bash
   python src/cli.py test
   ```

### Performance Optimization

1. **Adjust batch sizes** in `config.yaml`:
   ```yaml
   gmail:
     processing:
       batch_size: 25  # Reduce if experiencing timeouts
   ```

2. **Configure rate limiting**:
   ```yaml
   security:
     rate_limiting:
       requests_per_minute: 100  # Reduce if hitting API limits
   ```

## Security Considerations

- **API Keys**: Store securely and never commit to version control
- **OAuth Tokens**: Automatically managed and refreshed
- **Email Privacy**: Only email metadata is processed for classification
- **Local Storage**: All data stored locally in SQLite database

## Usage Examples

### Daily Email Management
```bash
# Start monitoring (run once in the morning)
python src/cli.py listen

# Check what was processed
python src/cli.py stats

# Clean up junk emails weekly
python src/cli.py junk
```

### Inbox Cleanup
```bash
# Process last month's emails
python src/cli.py batch --timeframe 1m

# Find and delete junk
python src/cli.py junk

# Backup database
python src/cli.py backup
```

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `python -m pytest tests/`
5. Submit a pull request

## License

This project is for educational and personal use. Ensure compliance with Gmail's Terms of Service and your organization's email policies.

---

**⚠️ Important Notes:**
- Always test with a small subset of emails first
- Backup your Gmail data before running batch operations
- Monitor the application logs for any issues
- This tool modifies your Gmail labels and moves emails - use with caution
