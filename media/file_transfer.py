"""File transfer module for AuraLink."""

import logging
import asyncio
import websockets
import os
from typing import Optional, Callable

logger = logging.getLogger(__name__)

CHUNK_SIZE = 65536
SERVER = "ws://127.0.0.1:8765"


class FileTransfer:
    """Handle file transfers over WebSocket."""
    
    @staticmethod
    async def send_file(file_path: str, server_uri: str = SERVER) -> bool:
        """
        Send a file to server.
        
        Args:
            file_path: Path to file to send
            server_uri: Server WebSocket URI
            
        Returns:
            True if successful
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
        
        try:
            async with websockets.connect(server_uri) as ws:
                file_size = os.path.getsize(file_path)
                file_name = os.path.basename(file_path)
                
                # Send metadata
                metadata = f"FILE:{file_name}:{file_size}"
                await ws.send(metadata)
                
                # Send file
                with open(file_path, "rb") as f:
                    while chunk := f.read(CHUNK_SIZE):
                        await ws.send(chunk)
                
                # Send EOF
                await ws.send(b"EOF")
                logger.info(f"File sent: {file_name}")
                return True
        
        except Exception as e:
            logger.error(f"File send error: {e}")
            return False
    
    @staticmethod
    async def receive_file(
        websocket,
        save_dir: str = "./received_files",
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        """
        Receive a file from WebSocket.
        
        Args:
            websocket: WebSocket connection
            save_dir: Directory to save received file
            progress_callback: Function called with (bytes_received, total_bytes)
            
        Returns:
            True if successful
        """
        try:
            os.makedirs(save_dir, exist_ok=True)
            
            # Get metadata
            metadata = await websocket.recv()
            if not metadata.startswith("FILE:"):
                logger.error("Invalid file metadata")
                return False
            
            parts = metadata.split(":")
            file_name = parts[1]
            file_size = int(parts[2])
            
            file_path = os.path.join(save_dir, file_name)
            bytes_received = 0
            
            with open(file_path, "wb") as f:
                while True:
                    chunk = await websocket.recv()
                    
                    if chunk == b"EOF":
                        break
                    
                    f.write(chunk)
                    bytes_received += len(chunk)
                    
                    if progress_callback:
                        progress_callback(bytes_received, file_size)
            
            logger.info(f"File received: {file_name}")
            return True
        
        except Exception as e:
            logger.error(f"File receive error: {e}")
            return False
