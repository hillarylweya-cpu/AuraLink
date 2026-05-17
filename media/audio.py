"""Audio streaming module for AuraLink."""

import logging
import socket
import asyncio
import pyaudio
from typing import Optional

logger = logging.getLogger(__name__)

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
HOST = "127.0.0.1"
AUDIO_PORT = 5000


class AudioStreamer:
    """Stream audio over UDP."""
    
    def __init__(self, chunk_size: int = CHUNK):
        self.chunk_size = chunk_size
        self.audio: Optional[pyaudio.PyAudio] = None
        self.stream: Optional[pyaudio.Stream] = None
        self.sock: Optional[socket.socket] = None
    
    def __enter__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logger.info("AudioStreamer initialized")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        if self.sock:
            self.sock.close()
        logger.info("AudioStreamer closed")
    
    async def stream_audio(self, target: tuple = (HOST, AUDIO_PORT)) -> None:
        """
        Stream audio to target.
        
        Args:
            target: Target (host, port) tuple
        """
        if not self.stream or not self.sock:
            logger.error("Streamer not initialized")
            return
        
        try:
            logger.info(f"Starting audio stream to {target}")
            while True:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.sock.sendto(data, target)
                await asyncio.sleep(0.001)
        
        except Exception as e:
            logger.error(f"Audio streaming error: {e}")
    
    def stop_streaming(self) -> None:
        """Stop audio streaming."""
        logger.info("Stopping audio stream")


class AudioReceiver:
    """Receive and playback audio over UDP."""
    
    def __init__(self, host: str = HOST, port: int = AUDIO_PORT):
        self.host = host
        self.port = port
        self.audio: Optional[pyaudio.PyAudio] = None
        self.stream: Optional[pyaudio.Stream] = None
        self.sock: Optional[socket.socket] = None
    
    def __enter__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            frames_per_buffer=CHUNK
        )
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        logger.info(f"AudioReceiver listening on {self.host}:{self.port}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        if self.sock:
            self.sock.close()
        logger.info("AudioReceiver closed")
    
    async def receive_audio(self) -> None:
        """Receive and playback audio."""
        if not self.sock or not self.stream:
            logger.error("Receiver not initialized")
            return
        
        try:
            logger.info("Receiving audio stream")
            while True:
                data, addr = self.sock.recvfrom(CHUNK)
                if data:
                    self.stream.write(data)
                await asyncio.sleep(0.001)
        
        except Exception as e:
            logger.error(f"Audio receive error: {e}")
