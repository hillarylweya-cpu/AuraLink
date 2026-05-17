"""WebSocket client module for AuraLink."""

import logging
import asyncio
import websockets
from typing import Callable, Optional
from websockets.client import WebSocketClientProtocol

logger = logging.getLogger(__name__)

SERVER = "ws://127.0.0.1:8765"
MAX_RETRIES = 5
RETRY_DELAY = 2


class WebSocketClient:
    """WebSocket client with auto-reconnection."""
    
    def __init__(self, server_uri: str = SERVER):
        self.server_uri = server_uri
        self.ws: Optional[WebSocketClientProtocol] = None
        self.connected = False
        self.retry_count = 0
    
    async def connect(self) -> bool:
        """
        Connect to WebSocket server with retry logic.
        
        Returns:
            True if connected successfully
        """
        while self.retry_count < MAX_RETRIES:
            try:
                self.ws = await websockets.connect(self.server_uri)
                self.connected = True
                self.retry_count = 0
                logger.info(f"Connected to {self.server_uri}")
                return True
            except Exception as e:
                self.retry_count += 1
                wait_time = RETRY_DELAY * (2 ** (self.retry_count - 1))
                logger.warning(f"Connection attempt {self.retry_count}/{MAX_RETRIES} failed: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
        
        logger.error(f"Failed to connect after {MAX_RETRIES} attempts")
        self.connected = False
        return False
    
    async def send_message(self, message: str) -> bool:
        """
        Send a message to the server.
        
        Args:
            message: Message to send
            
        Returns:
            True if sent successfully
        """
        if not self.connected or not self.ws:
            logger.warning("Not connected to server")
            return False
        
        try:
            await self.ws.send(message)
            logger.debug(f"Message sent: {message[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.connected = False
            return False
    
    async def receive_messages(self, callback: Callable[[str], None]) -> None:
        """
        Receive messages from server.
        
        Args:
            callback: Function to call with received messages
        """
        if not self.ws:
            logger.error("WebSocket not initialized")
            return
        
        try:
            async for message in self.ws:
                logger.debug(f"Message received: {message[:50]}...")
                callback(message)
        except Exception as e:
            logger.error(f"Error receiving messages: {e}")
            self.connected = False
    
    async def send_file(self, file_path: str, chunk_size: int = 1024) -> bool:
        """
        Send a file to the server.
        
        Args:
            file_path: Path to file
            chunk_size: Size of chunks to send
            
        Returns:
            True if sent successfully
        """
        if not self.connected or not self.ws:
            logger.warning("Not connected to server")
            return False
        
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    await self.ws.send(chunk)
            await self.ws.send(b"EOF")
            logger.info(f"File sent: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error sending file: {e}")
            return False
    
    async def close(self) -> None:
        """Close the WebSocket connection."""
        if self.ws:
            await self.ws.close()
            self.connected = False
            logger.info("WebSocket closed")


async def send_message(message: str) -> None:
    """Send a message to the default server."""
    client = WebSocketClient()
    if await client.connect():
        await client.send_message(message)
        await client.close()
