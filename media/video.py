"""Video streaming module for AuraLink."""

import logging
import asyncio
import socket
import pickle
import cv2
from typing import Optional, Callable

logger = logging.getLogger(__name__)

CHUNK_SIZE = 65536
HOST = "127.0.0.1"
VIDEO_PORT = 6000
DEFAULT_FPS = 30
RESIZE_SCALE = 0.5


class VideoStreamer:
    """Stream video over UDP."""
    
    def __init__(self, fps: int = DEFAULT_FPS, camera_index: int = 0):
        self.fps = fps
        self.camera_index = camera_index
        self.cap: Optional[cv2.VideoCapture] = None
        self.sock: Optional[socket.socket] = None
    
    def __enter__(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logger.info("VideoStreamer initialized")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cap:
            self.cap.release()
        if self.sock:
            self.sock.close()
        logger.info("VideoStreamer closed")
    
    async def stream_video(self, target: tuple = (HOST, VIDEO_PORT)) -> None:
        """
        Stream video frames.
        
        Args:
            target: Target (host, port) tuple
        """
        if not self.cap or not self.sock:
            logger.error("Streamer not initialized")
            return
        
        frame_delay = 1.0 / self.fps
        
        try:
            logger.info(f"Starting video stream to {target}")
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("Failed to read frame")
                    break
                
                # Resize frame
                frame = cv2.resize(frame, (0, 0), fx=RESIZE_SCALE, fy=RESIZE_SCALE)
                
                # Serialize and send
                data = pickle.dumps(frame)
                self.sock.sendto(data, target)
                self.sock.sendto(b"FRAME_END", target)
                
                await asyncio.sleep(frame_delay)
        
        except Exception as e:
            logger.error(f"Video streaming error: {e}")
    
    def stop_streaming(self) -> None:
        """Stop video streaming."""
        logger.info("Stopping video stream")


class VideoReceiver:
    """Receive video frames over UDP."""
    
    def __init__(self, host: str = HOST, port: int = VIDEO_PORT):
        self.host = host
        self.port = port
        self.sock: Optional[socket.socket] = None
    
    def __enter__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        logger.info(f"VideoReceiver listening on {self.host}:{self.port}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.sock:
            self.sock.close()
        logger.info("VideoReceiver closed")
    
    async def receive_video(self, callback: Callable[[cv2.Mat], None]) -> None:
        """
        Receive and process video frames.
        
        Args:
            callback: Function to call with each frame
        """
        if not self.sock:
            logger.error("Receiver not initialized")
            return
        
        try:
            logger.info("Receiving video stream")
            while True:
                data, addr = self.sock.recvfrom(CHUNK_SIZE)
                
                if data == b"FRAME_END":
                    continue
                
                try:
                    frame = pickle.loads(data)
                    callback(frame)
                except Exception as e:
                    logger.debug(f"Frame deserialization error: {e}")
                
                await asyncio.sleep(0.001)
        
        except Exception as e:
            logger.error(f"Video receive error: {e}")
