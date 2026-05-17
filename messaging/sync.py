"""Message synchronization module."""

import logging
import asyncio
from typing import Optional
from messaging.queue import get_pending, remove_pending
from networking.client import WebSocketClient

logger = logging.getLogger(__name__)

sync_task: Optional[asyncio.Task] = None
is_syncing = False


async def sync_pending() -> None:
    """
    Synchronize pending messages with server.
    Runs in background, checking every 5 seconds.
    """
    global is_syncing
    client = WebSocketClient()
    
    if not await client.connect():
        logger.error("Failed to connect for sync")
        return
    
    is_syncing = True
    try:
        while True:
            pending = get_pending()
            
            if pending:
                logger.info(f"Syncing {len(pending)} pending messages")
                for msg in pending:
                    if msg.should_retry():
                        try:
                            if await client.send_message(msg.content):
                                remove_pending(msg.id)
                                logger.info(f"Message synced: {msg.id}")
                            else:
                                msg.increment_retry()
                        except Exception as e:
                            logger.error(f"Sync error: {e}")
                            msg.increment_retry()
                    else:
                        logger.warning(f"Max retries exceeded for message: {msg.id}")
                        remove_pending(msg.id)
            
            await asyncio.sleep(5)
    
    except asyncio.CancelledError:
        logger.info("Sync task cancelled")
    except Exception as e:
        logger.error(f"Sync error: {e}")
    finally:
        await client.close()
        is_syncing = False


async def start_sync() -> None:
    """Start background message synchronization."""
    global sync_task
    if sync_task and not sync_task.done():
        logger.warning("Sync task already running")
        return
    
    sync_task = asyncio.create_task(sync_pending())
    logger.info("Sync task started")


async def stop_sync() -> None:
    """Stop background message synchronization."""
    global sync_task
    if sync_task and not sync_task.done():
        sync_task.cancel()
        try:
            await sync_task
        except asyncio.CancelledError:
            pass
        logger.info("Sync task stopped")


def get_sync_status() -> dict:
    """Get synchronization status."""
    return {
        "is_syncing": is_syncing,
        "task_running": sync_task is not None and not sync_task.done()
    }
