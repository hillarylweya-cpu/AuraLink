"""Database module for AuraLink - handles SQLite operations."""

import logging
import aiosqlite
from typing import List, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

DB_NAME = "aura.db"

# SQL Schema Definitions
CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    public_key TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_MESSAGES = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL,
    receiver TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    delivered INTEGER DEFAULT 0,
    synced INTEGER DEFAULT 0
)
"""


async def init_db() -> None:
    """Initialize database with required tables."""
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute(CREATE_USERS)
            await db.execute(CREATE_MESSAGES)
            await db.commit()
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise


async def save_message(sender: str, receiver: str, content: str) -> int:
    """
    Save a message to the database.
    
    Args:
        sender: Username of message sender
        receiver: Username of message receiver
        content: Message content
        
    Returns:
        Message ID
    """
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            cursor = await db.execute(
                """
                INSERT INTO messages
                (sender, receiver, content)
                VALUES (?, ?, ?)
                """,
                (sender, receiver, content)
            )
            await db.commit()
            logger.info(f"Message saved from {sender} to {receiver}")
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error saving message: {e}")
        raise


async def load_messages() -> List[Tuple[str, str, str, str]]:
    """
    Load all messages from database.
    
    Returns:
        List of (sender, receiver, content, timestamp) tuples
    """
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            cursor = await db.execute(
                "SELECT sender, receiver, content, timestamp FROM messages ORDER BY timestamp DESC"
            )
            messages = await cursor.fetchall()
            logger.info(f"Loaded {len(messages)} messages")
            return messages
    except Exception as e:
        logger.error(f"Error loading messages: {e}")
        return []


async def add_user(username: str, public_key: str) -> int:
    """
    Add a new user to the database.
    
    Args:
        username: User's username
        public_key: User's public encryption key
        
    Returns:
        User ID
    """
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            cursor = await db.execute(
                """
                INSERT INTO users (username, public_key)
                VALUES (?, ?)
                """,
                (username, public_key)
            )
            await db.commit()
            logger.info(f"User {username} added to database")
            return cursor.lastrowid
    except aiosqlite.IntegrityError:
        logger.warning(f"User {username} already exists")
        raise
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        raise


async def get_user_public_key(username: str) -> Optional[str]:
    """
    Get user's public key.
    
    Args:
        username: Username to look up
        
    Returns:
        Public key or None if user not found
    """
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            cursor = await db.execute(
                "SELECT public_key FROM users WHERE username = ?",
                (username,)
            )
            row = await cursor.fetchone()
            return row[0] if row else None
    except Exception as e:
        logger.error(f"Error getting user public key: {e}")
        return None


async def mark_message_delivered(message_id: int) -> bool:
    """
    Mark a message as delivered.
    
    Args:
        message_id: ID of message to mark
        
    Returns:
        True if successful
    """
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute(
                "UPDATE messages SET delivered = 1 WHERE id = ?",
                (message_id,)
            )
            await db.commit()
            return True
    except Exception as e:
        logger.error(f"Error marking message delivered: {e}")
        return False


async def get_undelivered_messages() -> List[Tuple]:
    """Get all undelivered messages."""
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            cursor = await db.execute(
                "SELECT id, sender, receiver, content FROM messages WHERE delivered = 0"
            )
            return await cursor.fetchall()
    except Exception as e:
        logger.error(f"Error getting undelivered messages: {e}")
        return []
