"""
AI Classifier for Email Categorization
Uses OpenAI GPT or local models to classify emails
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime

try:
    import openai
except ImportError:
    openai = None

from models import EmailCategory, EmailClassification


class AIClassifier:
    """AI-powered email classifier"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.classification_cache = {}
        
    async def initialize(self):
        """Initialize the AI classifier"""
        try:
            provider = self.config.get("provider", "openai")
            
            if provider == "openai":
                await self._initialize_openai()
            elif provider == "local":
                await self._initialize_local_model()
            else:
                raise ValueError(f"Unsupported AI provider: {provider}")
                
            self.logger.info(f"AI Classifier initialized with provider: {provider}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI classifier: {e}")
            raise
    
    async def _initialize_openai(self):
        """Initialize OpenAI client"""
        if openai is None:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
        
        # Get API key from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = openai.OpenAI(api_key=api_key)
        
        # Test the connection
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            self.logger.info("OpenAI connection test successful")
        except Exception as e:
            self.logger.error(f"OpenAI connection test failed: {e}")
            raise
    
    async def _initialize_local_model(self):
        """Initialize local AI model (placeholder for now)"""
        self.logger.warning("Local AI model not yet implemented, falling back to rule-based classification")
        # TODO: Implement local model initialization
        pass
    
    async def classify_email(self, email_data: Dict) -> EmailClassification:
        """Classify an email using AI"""
        try:
            # Check cache first
            cache_key = email_data.get("id", "")
            if cache_key in self.classification_cache:
                return self.classification_cache[cache_key]
            
            # Prepare email content for classification
            email_content = self._prepare_email_content(email_data)
            
            # Get classification
            if self.config.get("provider") == "openai" and self.client:
                classification = await self._classify_with_openai(email_content, email_data)
            else:
                # Fallback to rule-based classification
                classification = self._classify_with_rules(email_data)
            
            # Cache the result
            self.classification_cache[cache_key] = classification
            
            return classification
            
        except Exception as e:
            self.logger.error(f"Error classifying email: {e}")
            # Return unknown classification on error
            return EmailClassification(
                email_id=email_data.get("id", ""),
                category=EmailCategory.UNKNOWN,
                confidence=0.0,
                reasoning=f"Classification error: {str(e)}",
                timestamp=datetime.now()
            )
    
    def _prepare_email_content(self, email_data: Dict) -> str:
        """Prepare email content for AI classification"""
        sender = email_data.get("sender", "")
        subject = email_data.get("subject", "")
        body = email_data.get("body", "")[:1000]  # Limit body length
        
        return f"""
Email Details:
Sender: {sender}
Subject: {subject}
Body Preview: {body}
        """.strip()
    
    async def _classify_with_openai(self, email_content: str, email_data: Dict) -> EmailClassification:
        """Classify email using OpenAI"""
        try:
            prompt = self._build_classification_prompt(email_content)
            
            response = self.client.chat.completions.create(
                model=self.config.get("model", "gpt-4-turbo-preview"),
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.get("max_tokens", 1000),
                temperature=self.config.get("temperature", 0.1)
            )
            
            # Parse the response
            result = response.choices[0].message.content
            classification_data = json.loads(result)
            
            category = EmailCategory(classification_data["category"])
            confidence = float(classification_data["confidence"])
            reasoning = classification_data["reasoning"]
            
            return EmailClassification(
                email_id=email_data.get("id", ""),
                category=category,
                confidence=confidence,
                reasoning=reasoning,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"OpenAI classification error: {e}")
            # Fallback to rule-based
            return self._classify_with_rules(email_data)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for email classification"""
        return """
You are an email classification expert. Your task is to categorize emails into one of these categories:

1. IMPORTANT: Emails requiring immediate attention, action items, deadlines, meetings, work-related communications, financial matters, legal documents, urgent personal matters
2. PROMOTIONAL: Marketing emails, newsletters, sales offers, advertisements, promotional campaigns, shopping deals
3. SOCIAL: Social media notifications, friend requests, social platform updates, community notifications
4. JUNK: Spam, phishing attempts, suspicious emails, lottery scams, suspicious links, obvious fraud

Analyze the sender, subject, and content to make your decision.

Response format (JSON only):
{
    "category": "important|promotional|social|junk",
    "confidence": 0.85,
    "reasoning": "Brief explanation of classification decision"
}
        """.strip()
    
    def _build_classification_prompt(self, email_content: str) -> str:
        """Build the classification prompt"""
        return f"""
Please classify this email:

{email_content}

Consider:
- Sender reputation and domain
- Subject line keywords and urgency indicators
- Content type and purpose
- Potential security risks
- Business vs personal nature

Provide your classification in the specified JSON format.
        """.strip()
    
    def _classify_with_rules(self, email_data: Dict) -> EmailClassification:
        """Fallback rule-based classification"""
        sender = email_data.get("sender", "").lower()
        subject = email_data.get("subject", "").lower()
        body = email_data.get("body", "").lower()
        
        # Get classification keywords from config
        categories = self.config.get("classification", {}).get("categories", {})
        
        # Check for junk indicators first
        junk_keywords = categories.get("junk", {}).get("keywords", [])
        if any(keyword in subject or keyword in body or keyword in sender for keyword in junk_keywords):
            return EmailClassification(
                email_id=email_data.get("id", ""),
                category=EmailCategory.JUNK,
                confidence=0.8,
                reasoning="Matched junk keywords",
                timestamp=datetime.now()
            )
        
        # Check for promotional indicators
        promo_keywords = categories.get("promotional", {}).get("keywords", [])
        if any(keyword in subject or keyword in body for keyword in promo_keywords):
            return EmailClassification(
                email_id=email_data.get("id", ""),
                category=EmailCategory.PROMOTIONAL,
                confidence=0.7,
                reasoning="Matched promotional keywords",
                timestamp=datetime.now()
            )
        
        # Check for social indicators
        social_keywords = categories.get("social", {}).get("keywords", [])
        if any(keyword in sender or keyword in subject for keyword in social_keywords):
            return EmailClassification(
                email_id=email_data.get("id", ""),
                category=EmailCategory.SOCIAL,
                confidence=0.7,
                reasoning="Matched social keywords",
                timestamp=datetime.now()
            )
        
        # Check for important indicators
        important_keywords = categories.get("important", {}).get("keywords", [])
        important_senders = categories.get("important", {}).get("senders", [])
        
        if (any(keyword in subject or keyword in body for keyword in important_keywords) or
            any(sender_pattern in sender for sender_pattern in important_senders)):
            return EmailClassification(
                email_id=email_data.get("id", ""),
                category=EmailCategory.IMPORTANT,
                confidence=0.6,
                reasoning="Matched important keywords or senders",
                timestamp=datetime.now()
            )
        
        # Default to unknown
        return EmailClassification(
            email_id=email_data.get("id", ""),
            category=EmailCategory.UNKNOWN,
            confidence=0.3,
            reasoning="No clear classification found",
            timestamp=datetime.now()
        )
    
    async def cleanup(self):
        """Cleanup classifier resources"""
        self.classification_cache.clear()
        self.logger.info("AI Classifier cleaned up")
