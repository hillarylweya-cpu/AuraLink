"""Encryption module for AuraLink using PyNaCl."""

import logging
import base64
from typing import bytes, str, Tuple
from nacl.public import PrivateKey, PublicKey, Box
from nacl.utils import EncryptionError

logger = logging.getLogger(__name__)

# Generate or load keys
private_key = PrivateKey.generate()
public_key = private_key.public_key


class EncryptionManager:
    """Manage encryption/decryption operations."""
    
    def __init__(self):
        self.private_key = PrivateKey.generate()
        self.public_key = self.private_key.public_key
        logger.info("EncryptionManager initialized")
    
    def export_public_key(self) -> str:
        """
        Export public key as base64 string.
        
        Returns:
            Base64 encoded public key
        """
        return base64.b64encode(bytes(self.public_key)).decode()
    
    def import_public_key(self, key_str: str) -> PublicKey:
        """
        Import public key from base64 string.
        
        Args:
            key_str: Base64 encoded public key
            
        Returns:
            PublicKey object
        """
        try:
            key_bytes = base64.b64decode(key_str)
            return PublicKey(key_bytes)
        except Exception as e:
            logger.error(f"Error importing public key: {e}")
            raise
    
    def encrypt_message(self, recipient_public_key: PublicKey, message: str) -> str:
        """
        Encrypt a message for a recipient.
        
        Args:
            recipient_public_key: Recipient's public key
            message: Message to encrypt
            
        Returns:
            Base64 encoded encrypted message
        """
        try:
            box = Box(self.private_key, recipient_public_key)
            encrypted = box.encrypt(message.encode())
            return base64.b64encode(bytes(encrypted)).decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt_message(self, sender_public_key: PublicKey, encrypted_msg: str) -> str:
        """
        Decrypt a message from a sender.
        
        Args:
            sender_public_key: Sender's public key
            encrypted_msg: Base64 encoded encrypted message
            
        Returns:
            Decrypted message
        """
        try:
            box = Box(self.private_key, sender_public_key)
            encrypted_bytes = base64.b64decode(encrypted_msg)
            decrypted = box.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise


def encrypt_message(recipient_public: PublicKey, message: str) -> str:
    """
    Encrypt message using module-level keys.
    
    Args:
        recipient_public: Recipient's public key
        message: Message to encrypt
        
    Returns:
        Base64 encoded encrypted message
    """
    try:
        box = Box(private_key, recipient_public)
        encrypted = box.encrypt(message.encode())
        return base64.b64encode(bytes(encrypted)).decode()
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        raise


def decrypt_message(sender_public: PublicKey, encrypted: str) -> str:
    """
    Decrypt message using module-level keys.
    
    Args:
        sender_public: Sender's public key
        encrypted: Base64 encoded encrypted message
        
    Returns:
        Decrypted message
    """
    try:
        box = Box(private_key, sender_public)
        encrypted_bytes = base64.b64decode(encrypted)
        decrypted = box.decrypt(encrypted_bytes)
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise


def export_keys() -> Tuple[str, str]:
    """
    Export private and public keys.
    
    Returns:
        Tuple of (private_key_b64, public_key_b64)
    """
    return (
        base64.b64encode(bytes(private_key)).decode(),
        base64.b64encode(bytes(public_key)).decode()
    )
