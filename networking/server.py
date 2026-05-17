"""WebSocket server module for AuraLink."""

import logging
import asyncio
import websockets
from websockets.server import WebSocketServerProtocol
from typing import Set

logger = logging.getLogger(__name__)

clients: Set[WebSocketServerProtocol] = set()
HOST = "0.0.0.0"
PORT = 8765


async def handler(websocket: WebSocketServerProtocol) -> None:
    """
    Handle incoming WebSocket connections.
    
    Args:
        websocket: WebSocket connection object
    """
    client_addr = websocket.remote_address
    clients.add(websocket)
    logger.info(f"Client connected: {client_addr}")
    
    try:
        async for message in websocket:
            logger.debug(f"Received message from {client_addr}")
            # Broadcast to all other clients
            for client in clients:
                if client != websocket and client.open:
                    try:
                        await client.send(message)
                    except websockets.exceptions.ConnectionClosed:
                        logger.warning(f"Failed to send to {client.remote_address}")
                        clients.discard(client)
    
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client disconnected: {client_addr}")
    except Exception as e:
        logger.error(f"Handler error for {client_addr}: {e}")
    finally:
        clients.discard(websocket)
        logger.info(f"Cleanup: {client_addr} removed. Clients: {len(clients)}")


async def start_server(host: str = HOST, port: int = PORT) -> None:
    """
    Start WebSocket server.
    
    Args:
        host: Host address to bind to
        port: Port to bind to
    """
    try:
        async with websockets.serve(handler, host, port):
            logger.info(f"AuraLink WebSocket server started on {host}:{port}")
            await asyncio.Future()  # Run forever
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


def get_connected_clients() -> int:
    """Get number of connected clients."""
    return len(clients)
