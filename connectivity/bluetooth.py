"""Bluetooth scanning module for AuraLink."""

import logging
import asyncio
from typing import List, Optional
from bleak import BleakScanner, BLEDevice

logger = logging.getLogger(__name__)

DISCOVERY_TIMEOUT = 5


class BluetoothScanner:
    """Scan for Bluetooth devices."""
    
    @staticmethod
    async def discover_devices(timeout: int = DISCOVERY_TIMEOUT) -> List[BLEDevice]:
        """
        Discover Bluetooth devices.
        
        Args:
            timeout: Discovery timeout in seconds
            
        Returns:
            List of discovered devices
        """
        try:
            logger.info(f"Scanning for Bluetooth devices (timeout: {timeout}s)")
            devices = await BleakScanner.discover(timeout=timeout)
            logger.info(f"Found {len(devices)} device(s)")
            return devices
        
        except Exception as e:
            logger.error(f"Bluetooth discovery error: {e}")
            return []
    
    @staticmethod
    async def find_device_by_name(name: str, timeout: int = DISCOVERY_TIMEOUT) -> Optional[BLEDevice]:
        """
        Find a device by name.
        
        Args:
            name: Device name to search for
            timeout: Discovery timeout in seconds
            
        Returns:
            Device if found, None otherwise
        """
        try:
            devices = await BluetoothScanner.discover_devices(timeout)
            for device in devices:
                if device.name == name:
                    logger.info(f"Found device: {name}")
                    return device
            
            logger.warning(f"Device not found: {name}")
            return None
        
        except Exception as e:
            logger.error(f"Error finding device: {e}")
            return None
    
    @staticmethod
    async def find_device_by_address(address: str, timeout: int = DISCOVERY_TIMEOUT) -> Optional[BLEDevice]:
        """
        Find a device by MAC address.
        
        Args:
            address: Device MAC address
            timeout: Discovery timeout in seconds
            
        Returns:
            Device if found, None otherwise
        """
        try:
            devices = await BluetoothScanner.discover_devices(timeout)
            for device in devices:
                if device.address == address:
                    logger.info(f"Found device: {address}")
                    return device
            
            logger.warning(f"Device not found: {address}")
            return None
        
        except Exception as e:
            logger.error(f"Error finding device: {e}")
            return None
