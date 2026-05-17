"""Main AuraLink application."""

import asyncio
import logging
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock

from database.db import init_db, save_message, load_messages
from networking.client import send_message, WebSocketClient
from messaging.queue import queue_message, get_pending
from messaging.sync import start_sync, stop_sync
from security.encryption import EncryptionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load KV file
KV = Builder.load_file("ui/main.kv")


class AuraApp(App):
    """Main AuraLink application class."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.encryption_manager = None
        self.sync_task = None
    
    def build(self):
        """Build the application."""
        logger.info("Building AuraApp")
        
        try:
            # Initialize database
            asyncio.run(init_db())
            logger.info("Database initialized")
            
            # Initialize encryption
            self.encryption_manager = EncryptionManager()
            logger.info("Encryption initialized")
            
            # Load message history
            self._load_message_history()
            
            # Start background sync
            asyncio.run(start_sync())
            logger.info("Message sync started")
        
        except Exception as e:
            logger.error(f"Error building app: {e}")
        
        return KV
    
    def _load_message_history(self) -> None:
        """Load and display message history."""
        try:
            messages = asyncio.run(load_messages())
            for sender, receiver, content, timestamp in messages:
                self.root.ids.messages.text += f"[{timestamp}] {sender}: {content}\n"
            logger.info(f"Loaded {len(messages)} messages")
        except Exception as e:
            logger.error(f"Error loading message history: {e}")
    
    def send_chat(self) -> None:
        """Send a chat message."""
        msg = self.root.ids.input_box.text.strip()
        
        if not msg:
            return
        
        try:
            logger.info(f"Sending message: {msg}")
            
            # Display message
            self.root.ids.messages.text += f"[You]: {msg}\n"
            
            # Save to database
            asyncio.run(save_message("You", "Peer", msg))
            
            # Try to send
            try:
                asyncio.run(send_message(msg))
            except Exception as e:
                logger.warning(f"Send failed, queueing message: {e}")
                queue_message(msg, "Peer")
                self.root.ids.messages.text += "[System]: Message queued (offline)\n"
            
            # Clear input
            self.root.ids.input_box.text = ""
        
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.root.ids.messages.text += f"[Error]: {e}\n"
    
    def on_stop(self):
        """Clean up when app stops."""
        logger.info("Stopping AuraApp")
        try:
            asyncio.run(stop_sync())
        except Exception as e:
            logger.error(f"Error stopping sync: {e}")
        return True


if __name__ == "__main__":
    app = AuraApp()
    app.run()
