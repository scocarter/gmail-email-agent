"""
Notification Manager - Handles system notifications for important emails
"""

import logging
import asyncio
from typing import Dict
from datetime import datetime

try:
    from plyer import notification
except ImportError:
    notification = None

try:
    import pystray
    from PIL import Image
except ImportError:
    pystray = None
    Image = None


class NotificationManager:
    """Manages system notifications and tray integration"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.tray_icon = None
        self.notification_history = []
        
    async def send_important_email_notification(self, email_data: Dict, classification: Dict):
        """Send notification for important emails"""
        if not self.config.get("enabled", True):
            return
            
        try:
            sender = email_data.get("sender", "Unknown")
            subject = email_data.get("subject", "No Subject")
            
            # Create notification
            title = f"Important Email from {sender}"
            message = f"Subject: {subject}"
            
            # Send desktop notification
            if self.config.get("important_emails", {}).get("popup", True):
                await self._send_desktop_notification(title, message, urgency="critical")
            
            # Play sound if configured
            if self.config.get("important_emails", {}).get("sound", True):
                await self._play_notification_sound()
            
            # Add to history
            self.notification_history.append({
                "timestamp": datetime.now(),
                "type": "important_email",
                "title": title,
                "message": message,
                "email_id": email_data.get("id", "")
            })
            
            self.logger.info(f"Sent important email notification: {title}")
            
        except Exception as e:
            self.logger.error(f"Error sending important email notification: {e}")
    
    async def _send_desktop_notification(self, title: str, message: str, urgency: str = "normal"):
        """Send desktop notification"""
        try:
            if notification:
                notification.notify(
                    title=title,
                    message=message,
                    timeout=10,
                    app_name="Gmail Email Agent"
                )
            else:
                # Fallback to system notification
                await self._send_system_notification(title, message)
                
        except Exception as e:
            self.logger.error(f"Error sending desktop notification: {e}")
    
    async def _send_system_notification(self, title: str, message: str):
        """Send system notification using osascript (macOS)"""
        try:
            import subprocess
            script = f'''
            display notification "{message}" with title "{title}" sound name "Default"
            '''
            subprocess.run(['osascript', '-e', script], check=True)
            
        except Exception as e:
            self.logger.error(f"Error sending system notification: {e}")
    
    async def _play_notification_sound(self):
        """Play notification sound"""
        try:
            import subprocess
            subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'], check=True)
        except Exception as e:
            self.logger.debug(f"Could not play notification sound: {e}")
    
    def setup_system_tray(self):
        """Setup system tray icon"""
        if not self.config.get("system_tray", {}).get("enabled", True):
            return
            
        if not pystray or not Image:
            self.logger.warning("System tray dependencies not available")
            return
        
        try:
            # Create a simple icon (you can replace with actual icon file)
            image = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
            
            # Create tray icon
            self.tray_icon = pystray.Icon(
                "gmail_agent",
                image,
                menu=pystray.Menu(
                    pystray.MenuItem("Gmail Email Agent", lambda: None, enabled=False),
                    pystray.MenuItem("Show Stats", self._show_stats),
                    pystray.MenuItem("Quit", self._quit_application)
                )
            )
            
            # Run in background thread
            import threading
            tray_thread = threading.Thread(target=self.tray_icon.run)
            tray_thread.daemon = True
            tray_thread.start()
            
            self.logger.info("System tray icon created")
            
        except Exception as e:
            self.logger.error(f"Error setting up system tray: {e}")
    
    def _show_stats(self, icon, item):
        """Show agent statistics"""
        # This would show a simple dialog with stats
        # For now, just log
        self.logger.info("Stats requested from system tray")
    
    def _quit_application(self, icon, item):
        """Quit application"""
        self.logger.info("Quit requested from system tray")
        if self.tray_icon:
            self.tray_icon.stop()
    
    async def send_junk_summary_notification(self, junk_summaries: list):
        """Send notification about junk emails found"""
        if not junk_summaries:
            return
            
        try:
            count = len(junk_summaries)
            title = f"Found {count} Potential Junk Emails"
            message = "Review and confirm deletion in the application"
            
            await self._send_desktop_notification(title, message)
            
            self.logger.info(f"Sent junk summary notification for {count} emails")
            
        except Exception as e:
            self.logger.error(f"Error sending junk summary notification: {e}")
    
    def get_notification_history(self) -> list:
        """Get notification history"""
        return self.notification_history.copy()
    
    def clear_notification_history(self):
        """Clear notification history"""
        self.notification_history.clear()
        self.logger.info("Notification history cleared")
