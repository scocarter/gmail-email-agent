# 📧 Gmail Email Agent

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)

An intelligent Python-based service that automatically manages your Gmail inbox using AI-driven email classification. It categorizes emails into Important, Promotional, Social, and Junk categories, then takes appropriate actions like moving emails to specific folders or sending notifications for important messages.

![Gmail Email Agent Demo](https://via.placeholder.com/800x400/0066cc/ffffff?text=Gmail+Email+Agent+Demo)

## ✨ Key Features

- 🤖 **AI-Powered Classification**: Uses OpenAI GPT or rule-based classification
- ⚡ **Real-time Processing**: Listens for new emails and processes them automatically
- 📦 **Batch Processing**: Scan and reclassify past emails within specified timeframes
- 🗑️ **Junk Detection**: Identify potential spam/junk emails with user confirmation before deletion
- 🔔 **Smart Notifications**: Desktop notifications for important emails on macOS
- 💾 **Database Tracking**: SQLite database for tracking classifications and statistics
- 🎛️ **Three Operating Modes**:
  1. **Listener Mode**: Continuously monitors for new emails
  2. **Batch Processor Mode**: Processes historical emails
  3. **Junk Detector Mode**: Finds and manages junk emails

## 📋 Prerequisites

- **Python 3.8+** (recommended: 3.9 or higher)
- **macOS** (for notification features)
- **Gmail Account** with API access
- **OpenAI API Key** (optional, for AI classification)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/gmail-email-agent.git
cd gmail-email-agent
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements-minimal.txt
```

### 3. Configure Gmail API

1. **Create a Google Cloud Project:**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Gmail API

2. **Create OAuth Credentials:**
   - Go to "APIs & Services" > "Credentials"
   - Create "OAuth client ID" (Desktop application)
   - Download the JSON file as `config/credentials.json`

3. **Set up OAuth Consent Screen:**
   - Configure as "External" type
   - Add your Gmail address to test users

### 4. Configure OpenAI (Optional)

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Or create .env file
cp .env.example .env
# Edit .env with your API key
```

### 5. Test the Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Run authentication
python authenticate.py

# Test the system
python src/cli.py test
```

## 🎮 Usage

### Command Line Interface

```bash
# Activate virtual environment (always run this first)
source .venv/bin/activate

# Start monitoring emails
python src/cli.py listen

# Process past emails
python src/cli.py batch --timeframe 7d

# Find and review junk emails
python src/cli.py junk

# View statistics
python src/cli.py stats

# Get help
python src/cli.py --help
```

### Configuration

Edit `config/config.yaml` to customize:

- AI classification settings
- Email processing parameters
- Notification preferences
- Classification keywords and rules

## 📁 Project Structure

```
gmail-email-agent/
├── config/
│   ├── config.yaml              # Main configuration
│   ├── credentials.json.example # OAuth credentials template
│   └── credentials.json         # Your OAuth credentials (not in git)
├── src/
│   ├── __init__.py             # Package initialization
│   ├── models.py               # Data models
│   ├── email_agent.py          # Main agent orchestrator
│   ├── ai_classifier.py        # AI-powered email classification
│   ├── email_processor.py      # Gmail API email processing
│   ├── notification_manager.py # macOS notifications & system tray
│   ├── database_manager.py     # SQLite database management
│   ├── utils.py               # Utility functions
│   └── cli.py                 # Command-line interface
├── data/                       # Database storage (auto-created)
├── logs/                       # Log files (auto-created)
├── .env.example               # Environment variables template
├── requirements-minimal.txt   # Core Python dependencies
├── setup.py                   # Package installation script
└── README.md                  # This file
```

## 🔧 Setup Scripts

The project includes helpful setup scripts:

- `./setup_gmail_api.sh` - Sets up Gmail API credentials
- `./check_status.sh` - Checks setup status
- `./authenticate.py` - Handles OAuth authentication
- `./verify_setup.py` - Verifies complete setup

## 📊 Email Classification

### Categories

- **Important**: Work emails, deadlines, meetings, financial matters
- **Promotional**: Marketing emails, newsletters, sales offers
- **Social**: Social media notifications, friend requests
- **Junk**: Spam, phishing attempts, suspicious emails

### AI Classification

The system supports two modes:

1. **OpenAI Mode** (recommended):
   - Uses GPT models for intelligent classification
   - Requires `OPENAI_API_KEY` environment variable
   - More accurate but costs money per request

2. **Rule-based Mode**:
   - Uses keyword matching and heuristics
   - Free but less accurate
   - Automatically used if OpenAI is not configured

## 🔔 Notifications

- **Desktop Notifications**: Uses macOS notification system
- **Sound Alerts**: Plays system sounds for important emails
- **System Tray**: Shows agent status and statistics

## 🛡️ Security & Privacy

- **API Keys**: Stored securely as environment variables
- **OAuth Tokens**: Automatically managed and refreshed
- **Email Privacy**: Only email metadata is processed for classification
- **Local Storage**: All data stored locally in SQLite database
- **No Cloud Storage**: Your emails never leave your machine

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This project is for educational and personal use. Ensure compliance with Gmail's Terms of Service and your organization's email policies. Always test with a small subset of emails first and backup your Gmail data before running batch operations.

## 🆘 Support

- 📚 Check the detailed [setup guide](README.txt)
- 🐛 [Report issues](https://github.com/yourusername/gmail-email-agent/issues)
- 💡 [Request features](https://github.com/yourusername/gmail-email-agent/issues)

## 🏆 Acknowledgments

- Google Gmail API for email access
- OpenAI for AI classification capabilities
- The Python community for excellent libraries

---

**Made with ❤️ for intelligent email management**
