"""
Database Manager - Handles storage of email classifications and history
"""

import sqlite3
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class DatabaseManager:
    """Manages SQLite database for email agent data"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.db_path = config.get("path", "data/email_agent.db")
        self.connection = None
        
    async def initialize(self):
        """Initialize database and create tables"""
        try:
            # Create data directory if it doesn't exist
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            
            # Create tables
            await self._create_tables()
            
            self.logger.info(f"Database initialized: {self.db_path}")
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    async def _create_tables(self):
        """Create database tables"""
        try:
            cursor = self.connection.cursor()
            
            # Email classifications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_classifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_id TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    reasoning TEXT,
                    timestamp DATETIME NOT NULL,
                    processed BOOLEAN DEFAULT FALSE,
                    sender TEXT,
                    subject TEXT,
                    date DATETIME
                )
            """)
            
            # Processing statistics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    total_processed INTEGER DEFAULT 0,
                    important_count INTEGER DEFAULT 0,
                    promotional_count INTEGER DEFAULT 0,
                    social_count INTEGER DEFAULT 0,
                    junk_count INTEGER DEFAULT 0,
                    errors INTEGER DEFAULT 0
                )
            """)
            
            # Deletion log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deletion_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_id TEXT NOT NULL,
                    deletion_reason TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    restored BOOLEAN DEFAULT FALSE
                )
            """)
            
            # User feedback table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_id TEXT NOT NULL,
                    predicted_category TEXT NOT NULL,
                    actual_category TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    timestamp DATETIME NOT NULL
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_id ON email_classifications(email_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON email_classifications(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON email_classifications(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON processing_stats(date)")
            
            self.connection.commit()
            self.logger.info("Database tables created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating database tables: {e}")
            raise
    
    async def save_classification(self, classification):
        """Save email classification to database"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO email_classifications 
                (email_id, category, confidence, reasoning, timestamp, processed)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                classification.email_id,
                classification.category.value,
                classification.confidence,
                classification.reasoning,
                classification.timestamp,
                classification.processed
            ))
            
            self.connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error saving classification: {e}")
            raise
    
    async def get_classification(self, email_id: str) -> Optional[Dict]:
        """Get email classification by ID"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT * FROM email_classifications WHERE email_id = ?
            """, (email_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting classification: {e}")
            return None
    
    async def get_classifications_by_category(self, category: str, limit: int = 100) -> List[Dict]:
        """Get classifications by category"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT * FROM email_classifications 
                WHERE category = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (category, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Error getting classifications by category: {e}")
            return []
    
    async def update_processing_stats(self, stats: Dict):
        """Update daily processing statistics"""
        try:
            cursor = self.connection.cursor()
            today = datetime.now().date()
            
            cursor.execute("""
                INSERT OR REPLACE INTO processing_stats 
                (date, total_processed, important_count, promotional_count, social_count, junk_count, errors)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                today,
                stats.get("total_processed", 0),
                stats.get("important_count", 0),
                stats.get("promotional_count", 0),
                stats.get("social_count", 0),
                stats.get("junk_count", 0),
                stats.get("errors", 0)
            ))
            
            self.connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error updating processing stats: {e}")
    
    async def get_processing_stats(self, days: int = 7) -> List[Dict]:
        """Get processing statistics for last N days"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT * FROM processing_stats 
                WHERE date >= date('now', '-{} days')
                ORDER BY date DESC
            """.format(days))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Error getting processing stats: {e}")
            return []
    
    async def log_deletion(self, email_id: str, reason: str):
        """Log email deletion"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO deletion_log (email_id, deletion_reason, timestamp)
                VALUES (?, ?, ?)
            """, (email_id, reason, datetime.now()))
            
            self.connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error logging deletion: {e}")
    
    async def save_user_feedback(self, email_id: str, predicted: str, actual: str, confidence: float):
        """Save user feedback for learning"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO user_feedback 
                (email_id, predicted_category, actual_category, confidence, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (email_id, predicted, actual, confidence, datetime.now()))
            
            self.connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error saving user feedback: {e}")
    
    async def get_user_feedback(self, limit: int = 100) -> List[Dict]:
        """Get user feedback for analysis"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT * FROM user_feedback 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Error getting user feedback: {e}")
            return []
    
    async def get_classification_accuracy(self) -> Dict:
        """Calculate classification accuracy from user feedback"""
        try:
            cursor = self.connection.cursor()
            
            # Get total feedback
            cursor.execute("SELECT COUNT(*) as total FROM user_feedback")
            total = cursor.fetchone()["total"]
            
            if total == 0:
                return {"accuracy": 0.0, "total_feedback": 0}
            
            # Get correct predictions
            cursor.execute("""
                SELECT COUNT(*) as correct 
                FROM user_feedback 
                WHERE predicted_category = actual_category
            """)
            correct = cursor.fetchone()["correct"]
            
            accuracy = (correct / total) * 100 if total > 0 else 0.0
            
            return {
                "accuracy": accuracy,
                "correct_predictions": correct,
                "total_feedback": total,
                "incorrect_predictions": total - correct
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating accuracy: {e}")
            return {"accuracy": 0.0, "total_feedback": 0}
    
    async def cleanup_old_data(self, days: int = 90):
        """Clean up old data older than specified days"""
        try:
            cursor = self.connection.cursor()
            
            # Clean old classifications
            cursor.execute("""
                DELETE FROM email_classifications 
                WHERE timestamp < datetime('now', '-{} days')
            """.format(days))
            
            # Clean old stats (keep more stats, so use longer period)
            cursor.execute("""
                DELETE FROM processing_stats 
                WHERE date < date('now', '-{} days')
            """.format(days * 2))
            
            # Clean old deletion logs
            cursor.execute("""
                DELETE FROM deletion_log 
                WHERE timestamp < datetime('now', '-{} days')
            """.format(days))
            
            self.connection.commit()
            
            self.logger.info(f"Cleaned up data older than {days} days")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
    
    async def backup_database(self, backup_path: str):
        """Create database backup"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f"Database backed up to: {backup_path}")
            
        except Exception as e:
            self.logger.error(f"Error backing up database: {e}")
    
    async def get_database_info(self) -> Dict:
        """Get database information and statistics"""
        try:
            cursor = self.connection.cursor()
            
            # Get table sizes
            tables = ["email_classifications", "processing_stats", "deletion_log", "user_feedback"]
            table_info = {}
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()["count"]
                table_info[table] = count
            
            # Get database file size
            import os
            file_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            return {
                "database_path": self.db_path,
                "file_size_bytes": file_size,
                "table_counts": table_info
            }
            
        except Exception as e:
            self.logger.error(f"Error getting database info: {e}")
            return {}
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed")
