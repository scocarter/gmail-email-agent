"""
Utility functions for the Gmail Email Agent
"""

import logging
import logging.handlers
from datetime import datetime, timedelta
from typing import Dict
import re


def setup_logging(config: Dict) -> logging.Logger:
    """Setup logging configuration"""
    
    # Create logger
    logger = logging.getLogger("gmail_email_agent")
    logger.setLevel(getattr(logging, config.get("level", "INFO")))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    if config.get("console", True):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    log_file = config.get("file", "logs/email_agent.log")
    if log_file:
        # Create logs directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=_parse_size(config.get("max_size", "10MB")),
            backupCount=config.get("backup_count", 5)
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def _parse_size(size_str: str) -> int:
    """Parse size string like '10MB' to bytes"""
    size_str = size_str.upper()
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        return int(size_str)


def parse_timeframe(timeframe: str) -> datetime:
    """Parse timeframe string like '7d', '2w', '1m' to datetime"""
    now = datetime.now()
    
    # Extract number and unit
    match = re.match(r'(\d+)([dwmy])', timeframe.lower())
    if not match:
        raise ValueError(f"Invalid timeframe format: {timeframe}")
    
    amount = int(match.group(1))
    unit = match.group(2)
    
    if unit == 'd':  # days
        return now - timedelta(days=amount)
    elif unit == 'w':  # weeks
        return now - timedelta(weeks=amount)
    elif unit == 'm':  # months (approximate)
        return now - timedelta(days=amount * 30)
    elif unit == 'y':  # years (approximate)
        return now - timedelta(days=amount * 365)
    else:
        raise ValueError(f"Unsupported time unit: {unit}")


def format_email_summary(email_data: Dict) -> str:
    """Format email data for display"""
    sender = email_data.get("sender", "Unknown")
    subject = email_data.get("subject", "No Subject")
    date = email_data.get("date", datetime.now())
    snippet = email_data.get("snippet", "")
    
    # Truncate long fields
    if len(subject) > 50:
        subject = subject[:47] + "..."
    if len(snippet) > 100:
        snippet = snippet[:97] + "..."
    
    return f"""
From: {sender}
Subject: {subject}
Date: {date.strftime('%Y-%m-%d %H:%M')}
Preview: {snippet}
    """.strip()


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:252] + "..."
    
    return filename


def extract_domain(email_address: str) -> str:
    """Extract domain from email address"""
    try:
        if '@' in email_address:
            return email_address.split('@')[1].lower()
        return ""
    except:
        return ""


def is_business_hours() -> bool:
    """Check if current time is during business hours (9-17 weekdays)"""
    now = datetime.now()
    
    # Check if weekday (Monday=0, Sunday=6)
    if now.weekday() >= 5:  # Weekend
        return False
    
    # Check if business hours (9 AM to 5 PM)
    if 9 <= now.hour < 17:
        return True
    
    return False


def create_email_signature(stats: Dict) -> str:
    """Create email signature with processing stats"""
    total = stats.get("total_processed", 0)
    important = stats.get("important_count", 0)
    promotional = stats.get("promotional_count", 0)
    social = stats.get("social_count", 0)
    junk = stats.get("junk_count", 0)
    
    return f"""
Email Agent Processing Summary:
- Total Processed: {total}
- Important: {important}
- Promotional: {promotional}
- Social: {social}
- Junk: {junk}
    """.strip()


def validate_email_address(email: str) -> bool:
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def calculate_processing_rate(processed: int, time_period: timedelta) -> float:
    """Calculate processing rate (emails per hour)"""
    if time_period.total_seconds() == 0:
        return 0.0
    
    hours = time_period.total_seconds() / 3600
    return processed / hours if hours > 0 else 0.0


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def create_backup_filename(base_name: str) -> str:
    """Create backup filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = base_name.rsplit('.', 1) if '.' in base_name else (base_name, '')
    
    if ext:
        return f"{name}_backup_{timestamp}.{ext}"
    else:
        return f"{name}_backup_{timestamp}"


def is_urgent_keyword(text: str) -> bool:
    """Check if text contains urgent keywords"""
    urgent_keywords = [
        'urgent', 'asap', 'emergency', 'critical', 'immediate',
        'deadline', 'time-sensitive', 'priority', 'rush', 'important'
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in urgent_keywords)


def extract_phone_numbers(text: str) -> list:
    """Extract phone numbers from text"""
    # Pattern for various phone number formats
    pattern = r'(\+?1?[-.\s]?)?(\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})'
    matches = re.findall(pattern, text)
    return [''.join(match) for match in matches]


def clean_email_body(body: str) -> str:
    """Clean email body text for processing"""
    if not body:
        return ""
    
    # Remove excessive whitespace
    body = re.sub(r'\s+', ' ', body)
    
    # Remove common email artifacts
    body = re.sub(r'On .* wrote:', '', body)  # Remove "On ... wrote:" lines
    body = re.sub(r'From:.*?Subject:.*?Date:.*?\n', '', body, flags=re.DOTALL)  # Remove header blocks
    
    # Remove signature blocks
    body = re.sub(r'--\s*\n.*', '', body, flags=re.DOTALL)
    
    return body.strip()


def get_time_of_day() -> str:
    """Get current time of day category"""
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"
