"""
Data models for Gmail Email Agent
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List


class ProcessingMode(Enum):
    LISTENER = "listener"
    BATCH_PROCESSOR = "batch_processor"
    JUNK_DETECTOR = "junk_detector"


class EmailCategory(Enum):
    IMPORTANT = "important"
    PROMOTIONAL = "promotional"
    SOCIAL = "social"
    JUNK = "junk"
    UNKNOWN = "unknown"


@dataclass
class EmailClassification:
    email_id: str
    category: EmailCategory
    confidence: float
    reasoning: str
    timestamp: datetime
    processed: bool = False


@dataclass
class EmailSummary:
    email_id: str
    sender: str
    subject: str
    date: datetime
    category: EmailCategory
    confidence: float
    snippet: str
