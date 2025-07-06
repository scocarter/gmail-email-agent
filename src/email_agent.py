"""
Gmail Email Agent - Main Agent Class
Handles email processing, classification, and management
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import yaml

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ai_classifier import AIClassifier
from email_processor import EmailProcessor
from notification_manager import NotificationManager
from database_manager import DatabaseManager
from utils import setup_logging, parse_timeframe
from models import ProcessingMode, EmailCategory, EmailClassification, EmailSummary


class EmailAgent:
    """Main Email Agent class that orchestrates email processing"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.logger = setup_logging(self.config.get("logging", {}))
        
        # Initialize components
        self.gmail_service = None
        self.ai_classifier = AIClassifier(self.config.get("ai", {}))
        self.email_processor = EmailProcessor(self.config.get("gmail", {}))
        self.notification_manager = NotificationManager(self.config.get("notifications", {}))
        self.database_manager = DatabaseManager(self.config.get("database", {}))
        
        # State management
        self.running = False
        self.last_check = None
        self.processing_stats = {
            "total_processed": 0,
            "important_count": 0,
            "promotional_count": 0,
            "social_count": 0,
            "junk_count": 0,
            "errors": 0
        }
        
        self.logger.info("Email Agent initialized")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {config_path}")
            raise
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing configuration file: {e}")
            raise
    
    async def initialize(self):
        """Initialize all components and authenticate with Gmail"""
        try:
            # Initialize Gmail service
            self.gmail_service = await self._authenticate_gmail()
            
            # Initialize database
            await self.database_manager.initialize()
            
            # Initialize AI classifier
            await self.ai_classifier.initialize()
            
            # Test Gmail connection
            await self._test_gmail_connection()
            
            self.logger.info("Email Agent fully initialized and ready")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Email Agent: {e}")
            raise
    
    async def _authenticate_gmail(self):
        """Authenticate with Gmail API"""
        creds = None
        scopes = self.config["gmail"]["scopes"]
        
        # Load existing token
        token_file = self.config["gmail"]["token_file"]
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, scopes)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config["gmail"]["credentials_file"], scopes)
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    async def _test_gmail_connection(self):
        """Test Gmail API connection"""
        try:
            profile = self.gmail_service.users().getProfile(userId='me').execute()
            self.logger.info(f"Connected to Gmail for {profile['emailAddress']}")
        except HttpError as e:
            self.logger.error(f"Failed to connect to Gmail: {e}")
            raise
    
    async def start_listener_mode(self):
        """Start the email listener mode"""
        self.logger.info("Starting listener mode...")
        self.running = True
        
        check_interval = self.config["modes"]["listener"]["check_interval"]
        
        while self.running:
            try:
                await self._process_new_emails()
                await asyncio.sleep(check_interval)
                
            except KeyboardInterrupt:
                self.logger.info("Received interrupt signal, stopping...")
                break
            except Exception as e:
                self.logger.error(f"Error in listener mode: {e}")
                await asyncio.sleep(check_interval)
    
    async def _process_new_emails(self):
        """Process new emails since last check"""
        try:
            # Get new emails
            query = self._build_new_email_query()
            new_emails = await self._get_emails(query)
            
            if not new_emails:
                return
            
            self.logger.info(f"Found {len(new_emails)} new emails to process")
            
            # Process emails in batches
            batch_size = self.config["gmail"]["processing"]["batch_size"]
            for i in range(0, len(new_emails), batch_size):
                batch = new_emails[i:i + batch_size]
                await self._process_email_batch(batch)
            
            # Update last check time
            self.last_check = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error processing new emails: {e}")
            self.processing_stats["errors"] += 1
    
    def _build_new_email_query(self) -> str:
        """Build Gmail query for new emails"""
        if self.last_check:
            # Get emails since last check
            timestamp = int(self.last_check.timestamp())
            return f"in:inbox after:{timestamp}"
        else:
            # First run - get emails from last hour
            one_hour_ago = datetime.now() - timedelta(hours=1)
            timestamp = int(one_hour_ago.timestamp())
            return f"in:inbox after:{timestamp}"
    
    async def _get_emails(self, query: str, max_results: int = None) -> List[Dict]:
        """Get emails from Gmail using query"""
        try:
            max_results = max_results or self.config["gmail"]["processing"]["max_emails_per_run"]
            
            result = self.gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = result.get('messages', [])
            
            # Get full email details
            emails = []
            for msg in messages:
                email_detail = self.gmail_service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                emails.append(email_detail)
            
            return emails
            
        except HttpError as e:
            self.logger.error(f"Error getting emails: {e}")
            return []
    
    async def _process_email_batch(self, emails: List[Dict]):
        """Process a batch of emails"""
        tasks = []
        
        for email in emails:
            task = asyncio.create_task(self._process_single_email(email))
            tasks.append(task)
        
        # Process batch concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle results
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Error processing email: {result}")
                self.processing_stats["errors"] += 1
    
    async def _process_single_email(self, email: Dict) -> EmailClassification:
        """Process a single email"""
        try:
            # Extract email details
            email_data = self.email_processor.extract_email_data(email)
            
            # Classify email using AI
            classification = await self.ai_classifier.classify_email(email_data)
            
            # Save classification to database
            await self.database_manager.save_classification(classification)
            
            # Apply Gmail labels/actions based on classification
            await self._apply_email_actions(email_data, classification)
            
            # Send notifications if needed
            await self._handle_notifications(email_data, classification)
            
            # Update statistics
            self._update_stats(classification)
            
            return classification
            
        except Exception as e:
            self.logger.error(f"Error processing email {email.get('id', 'unknown')}: {e}")
            raise
    
    async def _apply_email_actions(self, email_data: Dict, classification: EmailClassification):
        """Apply appropriate actions based on email classification"""
        email_id = email_data["id"]
        
        try:
            if classification.category == EmailCategory.PROMOTIONAL:
                await self._move_to_promotions(email_id)
            elif classification.category == EmailCategory.SOCIAL:
                await self._move_to_social(email_id)
            elif classification.category == EmailCategory.JUNK:
                # Don't auto-delete junk, just mark for review
                await self._mark_as_junk(email_id)
            # Important emails stay in inbox
            
        except Exception as e:
            self.logger.error(f"Error applying actions to email {email_id}: {e}")
    
    async def _move_to_promotions(self, email_id: str):
        """Move email to Promotions tab"""
        try:
            self.gmail_service.users().messages().modify(
                userId='me',
                id=email_id,
                body={
                    'addLabelIds': ['CATEGORY_PROMOTIONS'],
                    'removeLabelIds': ['INBOX']
                }
            ).execute()
            
        except HttpError as e:
            self.logger.error(f"Error moving email to promotions: {e}")
    
    async def _move_to_social(self, email_id: str):
        """Move email to Social tab"""
        try:
            self.gmail_service.users().messages().modify(
                userId='me',
                id=email_id,
                body={
                    'addLabelIds': ['CATEGORY_SOCIAL'],
                    'removeLabelIds': ['INBOX']
                }
            ).execute()
            
        except HttpError as e:
            self.logger.error(f"Error moving email to social: {e}")
    
    async def _mark_as_junk(self, email_id: str):
        """Mark email as junk (but don't delete)"""
        try:
            # Create custom junk label if it doesn't exist
            await self._ensure_junk_label_exists()
            
            self.gmail_service.users().messages().modify(
                userId='me',
                id=email_id,
                body={
                    'addLabelIds': ['JUNK_REVIEW'],
                    'removeLabelIds': ['INBOX']
                }
            ).execute()
            
        except HttpError as e:
            self.logger.error(f"Error marking email as junk: {e}")
    
    async def _ensure_junk_label_exists(self):
        """Ensure the JUNK_REVIEW label exists"""
        try:
            # Check if label exists
            labels = self.gmail_service.users().labels().list(userId='me').execute()
            
            junk_label_exists = any(
                label.get('name') == 'JUNK_REVIEW' 
                for label in labels.get('labels', [])
            )
            
            if not junk_label_exists:
                # Create the label
                label_object = {
                    'name': 'JUNK_REVIEW',
                    'labelListVisibility': 'labelShow',
                    'messageListVisibility': 'show'
                }
                
                self.gmail_service.users().labels().create(
                    userId='me',
                    body=label_object
                ).execute()
                
                self.logger.info("Created JUNK_REVIEW label")
                
        except HttpError as e:
            self.logger.error(f"Error managing junk label: {e}")
    
    async def _handle_notifications(self, email_data: Dict, classification: EmailClassification):
        """Handle notifications based on email classification"""
        if classification.category == EmailCategory.IMPORTANT:
            await self.notification_manager.send_important_email_notification(
                email_data, classification
            )
    
    def _update_stats(self, classification: EmailClassification):
        """Update processing statistics"""
        self.processing_stats["total_processed"] += 1
        
        if classification.category == EmailCategory.IMPORTANT:
            self.processing_stats["important_count"] += 1
        elif classification.category == EmailCategory.PROMOTIONAL:
            self.processing_stats["promotional_count"] += 1
        elif classification.category == EmailCategory.SOCIAL:
            self.processing_stats["social_count"] += 1
        elif classification.category == EmailCategory.JUNK:
            self.processing_stats["junk_count"] += 1
    
    async def run_batch_processor(self, timeframe: str = "7d"):
        """Run batch processor for past emails"""
        self.logger.info(f"Starting batch processor for timeframe: {timeframe}")
        
        try:
            # Parse timeframe and build query
            start_date = parse_timeframe(timeframe)
            query = f"in:inbox after:{int(start_date.timestamp())}"
            
            # Get emails
            emails = await self._get_emails(query)
            
            if not emails:
                self.logger.info("No emails found for batch processing")
                return
            
            self.logger.info(f"Processing {len(emails)} emails in batch mode")
            
            # Process in batches
            batch_size = self.config["modes"]["batch_processor"]["batch_size"]
            for i in range(0, len(emails), batch_size):
                batch = emails[i:i + batch_size]
                await self._process_email_batch(batch)
                
                # Brief pause between batches
                await asyncio.sleep(1)
            
            self.logger.info("Batch processing completed")
            
        except Exception as e:
            self.logger.error(f"Error in batch processor: {e}")
            raise
    
    async def run_junk_detector(self) -> List[EmailSummary]:
        """Run junk detector and return summary of potential junk emails"""
        self.logger.info("Starting junk detector...")
        
        try:
            # Get emails marked as junk or suspicious
            query = "label:JUNK_REVIEW OR (in:inbox AND (subject:spam OR subject:suspicious))"
            emails = await self._get_emails(query)
            
            if not emails:
                self.logger.info("No potential junk emails found")
                return []
            
            # Process and create summaries
            summaries = []
            for email in emails:
                try:
                    email_data = self.email_processor.extract_email_data(email)
                    classification = await self.ai_classifier.classify_email(email_data)
                    
                    if classification.category == EmailCategory.JUNK:
                        summary = EmailSummary(
                            email_id=email_data["id"],
                            sender=email_data["sender"],
                            subject=email_data["subject"],
                            date=email_data["date"],
                            category=classification.category,
                            confidence=classification.confidence,
                            snippet=email_data["snippet"]
                        )
                        summaries.append(summary)
                        
                except Exception as e:
                    self.logger.error(f"Error processing email in junk detector: {e}")
            
            self.logger.info(f"Found {len(summaries)} potential junk emails")
            return summaries
            
        except Exception as e:
            self.logger.error(f"Error in junk detector: {e}")
            raise
    
    async def delete_confirmed_junk(self, email_ids: List[str]):
        """Delete emails confirmed as junk by user"""
        self.logger.info(f"Deleting {len(email_ids)} confirmed junk emails")
        
        try:
            for email_id in email_ids:
                # Move to trash (Gmail doesn't have permanent delete via API)
                self.gmail_service.users().messages().trash(
                    userId='me',
                    id=email_id
                ).execute()
                
                # Log the deletion
                await self.database_manager.log_deletion(email_id, "junk")
            
            self.logger.info(f"Successfully deleted {len(email_ids)} junk emails")
            
        except Exception as e:
            self.logger.error(f"Error deleting junk emails: {e}")
            raise
    
    async def get_processing_stats(self) -> Dict:
        """Get current processing statistics"""
        return {
            **self.processing_stats,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "running": self.running
        }
    
    async def stop(self):
        """Stop the email agent"""
        self.logger.info("Stopping Email Agent...")
        self.running = False
        
        # Cleanup
        await self.database_manager.close()
        await self.ai_classifier.cleanup()
        
        self.logger.info("Email Agent stopped")


# Example usage
async def main():
    agent = EmailAgent()
    
    try:
        await agent.initialize()
        
        # Run in listener mode
        await agent.start_listener_mode()
        
    except KeyboardInterrupt:
        print("\nReceived interrupt signal")
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
