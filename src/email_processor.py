"""
Email Processor - Handles email data extraction and processing
"""

import base64
import email
import re
from datetime import datetime
from typing import Dict, List, Optional
import logging

try:
    from bs4 import BeautifulSoup
    import html2text
except ImportError:
    BeautifulSoup = None
    html2text = None


class EmailProcessor:
    """Processes Gmail email data"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize HTML to text converter if available
        if html2text:
            self.html_converter = html2text.HTML2Text()
            self.html_converter.ignore_links = True
            self.html_converter.ignore_images = True
        else:
            self.html_converter = None
    
    def extract_email_data(self, gmail_message: Dict) -> Dict:
        """Extract structured data from Gmail message"""
        try:
            # Get basic message info
            message_id = gmail_message.get('id', '')
            thread_id = gmail_message.get('threadId', '')
            
            # Extract headers
            headers = self._extract_headers(gmail_message)
            
            # Extract body
            body_text, body_html = self._extract_body(gmail_message)
            
            # Get snippet
            snippet = gmail_message.get('snippet', '')
            
            # Parse date
            date = self._parse_date(headers.get('Date', ''))
            
            return {
                'id': message_id,
                'thread_id': thread_id,
                'sender': headers.get('From', ''),
                'recipient': headers.get('To', ''),
                'cc': headers.get('Cc', ''),
                'bcc': headers.get('Bcc', ''),
                'subject': headers.get('Subject', ''),
                'date': date,
                'body': body_text,
                'body_html': body_html,
                'snippet': snippet,
                'labels': gmail_message.get('labelIds', []),
                'size_estimate': gmail_message.get('sizeEstimate', 0),
                'headers': headers
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting email data: {e}")
            return {
                'id': gmail_message.get('id', ''),
                'sender': '',
                'subject': '',
                'body': '',
                'date': datetime.now(),
                'snippet': gmail_message.get('snippet', ''),
                'error': str(e)
            }
    
    def _extract_headers(self, gmail_message: Dict) -> Dict[str, str]:
        """Extract email headers"""
        headers = {}
        
        try:
            payload = gmail_message.get('payload', {})
            header_list = payload.get('headers', [])
            
            for header in header_list:
                name = header.get('name', '')
                value = header.get('value', '')
                headers[name] = value
                
        except Exception as e:
            self.logger.error(f"Error extracting headers: {e}")
        
        return headers
    
    def _extract_body(self, gmail_message: Dict) -> tuple[str, str]:
        """Extract email body (text and HTML)"""
        try:
            payload = gmail_message.get('payload', {})
            
            body_text = ""
            body_html = ""
            
            # Handle different message structures
            if 'parts' in payload:
                # Multipart message
                body_text, body_html = self._extract_multipart_body(payload['parts'])
            else:
                # Single part message
                body_data = payload.get('body', {}).get('data', '')
                mime_type = payload.get('mimeType', '')
                
                if body_data:
                    decoded_body = self._decode_base64(body_data)
                    
                    if mime_type == 'text/plain':
                        body_text = decoded_body
                    elif mime_type == 'text/html':
                        body_html = decoded_body
                        body_text = self._html_to_text(decoded_body)
            
            return body_text, body_html
            
        except Exception as e:
            self.logger.error(f"Error extracting body: {e}")
            return "", ""
    
    def _extract_multipart_body(self, parts: List[Dict]) -> tuple[str, str]:
        """Extract body from multipart message"""
        body_text = ""
        body_html = ""
        
        for part in parts:
            mime_type = part.get('mimeType', '')
            
            if mime_type == 'text/plain':
                body_data = part.get('body', {}).get('data', '')
                if body_data:
                    body_text += self._decode_base64(body_data)
                    
            elif mime_type == 'text/html':
                body_data = part.get('body', {}).get('data', '')
                if body_data:
                    html_content = self._decode_base64(body_data)
                    body_html += html_content
                    if not body_text:  # Only convert if no plain text
                        body_text += self._html_to_text(html_content)
                        
            elif 'parts' in part:
                # Nested multipart
                nested_text, nested_html = self._extract_multipart_body(part['parts'])
                body_text += nested_text
                body_html += nested_html
        
        return body_text, body_html
    
    def _decode_base64(self, data: str) -> str:
        """Decode base64 encoded email data"""
        try:
            # Gmail uses URL-safe base64 encoding
            decoded_bytes = base64.urlsafe_b64decode(data + '===')  # Add padding
            return decoded_bytes.decode('utf-8', errors='ignore')
        except Exception as e:
            self.logger.error(f"Error decoding base64: {e}")
            return ""
    
    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML to plain text"""
        if not html_content:
            return ""
        
        try:
            if self.html_converter:
                # Use html2text library
                return self.html_converter.handle(html_content)
            elif BeautifulSoup:
                # Use BeautifulSoup as fallback
                soup = BeautifulSoup(html_content, 'html.parser')
                return soup.get_text(separator=' ', strip=True)
            else:
                # Basic HTML tag removal
                return self._strip_html_tags(html_content)
                
        except Exception as e:
            self.logger.error(f"Error converting HTML to text: {e}")
            return self._strip_html_tags(html_content)
    
    def _strip_html_tags(self, html_content: str) -> str:
        """Basic HTML tag removal"""
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', html_content)
        # Remove extra whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text)
        return clean_text.strip()
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse email date string"""
        if not date_str:
            return datetime.now()
        
        try:
            # Parse RFC 2822 date format
            parsed_date = email.utils.parsedate_to_datetime(date_str)
            return parsed_date
        except Exception as e:
            self.logger.error(f"Error parsing date '{date_str}': {e}")
            return datetime.now()
    
    def extract_sender_info(self, sender_str: str) -> Dict[str, str]:
        """Extract sender name and email from sender string"""
        try:
            # Parse "Name <email@domain.com>" format
            match = re.match(r'^(.+?)\s*<(.+?)>$', sender_str.strip())
            if match:
                name = match.group(1).strip().strip('"')
                email_addr = match.group(2).strip()
            else:
                # Just email address
                name = ""
                email_addr = sender_str.strip()
            
            # Extract domain
            domain = ""
            if '@' in email_addr:
                domain = email_addr.split('@')[1]
            
            return {
                'name': name,
                'email': email_addr,
                'domain': domain
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing sender info: {e}")
            return {
                'name': "",
                'email': sender_str,
                'domain': ""
            }
    
    def is_automated_email(self, email_data: Dict) -> bool:
        """Check if email appears to be automated/bulk"""
        try:
            headers = email_data.get('headers', {})
            sender = email_data.get('sender', '').lower()
            subject = email_data.get('subject', '').lower()
            
            # Check for automated indicators
            automated_indicators = [
                'no-reply',
                'noreply',
                'do-not-reply',
                'donotreply',
                'automated',
                'auto-generated',
                'notification',
                'alerts'
            ]
            
            # Check sender
            if any(indicator in sender for indicator in automated_indicators):
                return True
            
            # Check headers
            if headers.get('Precedence', '').lower() == 'bulk':
                return True
            
            if 'List-Unsubscribe' in headers:
                return True
            
            # Check for bulk mail headers
            bulk_headers = [
                'X-Bulk-Mail',
                'X-Campaign-Id',
                'X-Mailgun-Tag',
                'X-SES-Message-Source'
            ]
            
            if any(header in headers for header in bulk_headers):
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking if email is automated: {e}")
            return False
    
    def extract_links(self, email_data: Dict) -> List[str]:
        """Extract links from email content"""
        links = []
        
        try:
            body_html = email_data.get('body_html', '')
            body_text = email_data.get('body', '')
            
            # Extract from HTML if available
            if body_html and BeautifulSoup:
                soup = BeautifulSoup(body_html, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith(('http://', 'https://')):
                        links.append(href)
            
            # Extract from text using regex
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+[^\s<>"{}|\\^`\[\].,;:!?]'
            text_links = re.findall(url_pattern, body_text)
            links.extend(text_links)
            
            # Remove duplicates
            links = list(set(links))
            
        except Exception as e:
            self.logger.error(f"Error extracting links: {e}")
        
        return links
    
    def get_email_priority(self, email_data: Dict) -> str:
        """Determine email priority based on headers and content"""
        try:
            headers = email_data.get('headers', {})
            subject = email_data.get('subject', '').lower()
            
            # Check priority headers
            priority = headers.get('X-Priority', '')
            importance = headers.get('Importance', '').lower()
            
            if priority == '1' or importance == 'high':
                return 'high'
            elif priority in ['4', '5'] or importance == 'low':
                return 'low'
            
            # Check subject for urgency indicators
            urgent_words = ['urgent', 'asap', 'emergency', 'critical', 'immediate']
            if any(word in subject for word in urgent_words):
                return 'high'
            
            return 'normal'
            
        except Exception as e:
            self.logger.error(f"Error determining email priority: {e}")
            return 'normal'
