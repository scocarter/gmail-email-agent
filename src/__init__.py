"""
Gmail Email Agent - Intelligent Email Management System
"""

__version__ = "1.0.0"
__author__ = "Gmail Agent Team"
__description__ = "AI-powered Gmail inbox management and organization"

from .email_agent import EmailAgent, EmailCategory, EmailClassification, EmailSummary
from .ai_classifier import AIClassifier
from .email_processor import EmailProcessor
from .notification_manager import NotificationManager
from .database_manager import DatabaseManager

__all__ = [
    'EmailAgent',
    'EmailCategory', 
    'EmailClassification',
    'EmailSummary',
    'AIClassifier',
    'EmailProcessor',
    'NotificationManager',
    'DatabaseManager'
]
