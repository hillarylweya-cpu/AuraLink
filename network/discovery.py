"""Service discovery module using Zeroconf."""

import logging
import socket
from typing import Optional
from zeroconf import Zeroconf, ServiceInfo

logger = logging.getLogger(__name__)

SERVICE_TYPE = "_auralink._tcp.local."
SERVICE_NAME = "AuraLink"
DEFAULT_PORT = 8765


class ServiceDiscovery:
    """Handle Zeroconf service registration and discovery."""
    
    def __init__(self, port: int = DEFAULT_PORT):
        self.port = port
        self.zeroconf: Optional[Zeroconf] = None
        self.service_info: Optional[ServiceInfo] = None
    
    def register_service(self, hostname: str = "127.0.0.1") -> bool:
        """
        Register service on the local network.
        
        Args:
            hostname: Host address or IP
            
        Returns:
            True if successful
        """
        try:
            self.zeroconf = Zeroconf()
            
            # Convert hostname to IP if needed
            try:
                addresses = [socket.inet_aton(hostname)]
            except socket.error:
                # If not an IP, resolve it
                addresses = [socket.inet_aton(socket.gethostbyname(hostname))]
            
            self.service_info = ServiceInfo(
                SERVICE_TYPE,
                f"{SERVICE_NAME}.{SERVICE_TYPE}",
                addresses=addresses,
                port=self.port,
                properties={"version": "1.0"},
            )
            
            self.zeroconf.register_service(self.service_info)
            logger.info(f"Service registered: {SERVICE_NAME} on port {self.port}")
            return True
        
        except Exception as e:
            logger.error(f"Service registration error: {e}")
            return False
    
    def unregister_service(self) -> bool:
        """
        Unregister service from the network.
        
        Returns:
            True if successful
        """
        try:
            if self.service_info and self.zeroconf:
                self.zeroconf.unregister_service(self.service_info)
                logger.info("Service unregistered")
            return True
        except Exception as e:
            logger.error(f"Service unregistration error: {e}")
            return False
    
    def close(self) -> None:
        """Close Zeroconf connection."""
        if self.zeroconf:
            self.unregister_service()
            self.zeroconf.close()
            logger.info("Zeroconf closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
