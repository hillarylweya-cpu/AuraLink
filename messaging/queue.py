"""Message queue module for offline message handling."""

import logging
from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PendingMessage:
    """Represents a pending message."""
    id: str
    content: str
    recipient: str
    created_at: datetime = field(default_factory=datetime.now)
    retry_count: int = 0
    max_retries: int = 5
    
    def should_retry(self) -> bool:
        """Check if message should be retried."""
        return self.retry_count < self.max_retries
    
    def increment_retry(self) -> None:
        """Increment retry count."""
        self.retry_count += 1


pending_messages: List[PendingMessage] = []


def queue_message(msg: str, recipient: str = "Peer") -> str:
    """
    Add a message to the pending queue.
    
    Args:
        msg: Message content
        recipient: Message recipient
        
    Returns:
        Message ID
    """
    msg_id = f"{len(pending_messages)}_{datetime.now().timestamp()}"
    pending = PendingMessage(id=msg_id, content=msg, recipient=recipient)
    pending_messages.append(pending)
    logger.info(f"Message queued: {msg_id}")
    return msg_id


def get_pending() -> List[PendingMessage]:
    """Get all pending messages."""
    return pending_messages.copy()


def get_pending_count() -> int:
    """Get count of pending messages."""
    return len(pending_messages)


def remove_pending(msg_id: str) -> bool:
    """
    Remove a pending message.
    
    Args:
        msg_id: ID of message to remove
        
    Returns:
        True if removed
    """
    global pending_messages
    for i, msg in enumerate(pending_messages):
        if msg.id == msg_id:
            pending_messages.pop(i)
            logger.info(f"Message removed: {msg_id}")
            return True
    return False


def clear_pending() -> None:
    """Clear all pending messages."""
    global pending_messages
    count = len(pending_messages)
    pending_messages.clear()
    logger.info(f"Cleared {count} pending messages")


def get_message_by_id(msg_id: str) -> Optional[PendingMessage]:
    """
    Get a pending message by ID.
    
    Args:
        msg_id: ID of message
        
    Returns:
        Message or None if not found
    """
    for msg in pending_messages:
        if msg.id == msg_id:
            return msg
    return None


def get_pending_by_recipient(recipient: str) -> List[PendingMessage]:
    """
    Get pending messages for a specific recipient.
    
    Args:
        recipient: Recipient name
        
    Returns:
        List of pending messages
    """
    return [msg for msg in pending_messages if msg.recipient == recipient]
