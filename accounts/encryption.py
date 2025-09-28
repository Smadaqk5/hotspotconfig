import base64
import os
from cryptography.fernet import Fernet
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""
    
    def __init__(self):
        # Get encryption key from settings or generate one
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self):
        """Get encryption key from environment or generate one"""
        key = getattr(settings, 'ENCRYPTION_KEY', None)
        if not key:
            # Generate a new key (in production, this should be set in environment)
            key = Fernet.generate_key()
            logger.warning("No ENCRYPTION_KEY found in settings. Generated new key. "
                          "Set ENCRYPTION_KEY in your environment variables for production.")
        else:
            # Convert string key to bytes if needed
            if isinstance(key, str):
                key = key.encode()
        return key
    
    def encrypt(self, data):
        """Encrypt sensitive data"""
        if not data:
            return None
        
        try:
            # Convert to bytes if string
            if isinstance(data, str):
                data = data.encode()
            
            encrypted_data = self.cipher.encrypt(data)
            # Return base64 encoded string for database storage
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return None
    
    def decrypt(self, encrypted_data):
        """Decrypt sensitive data"""
        if not encrypted_data:
            return None
        
        try:
            # Decode base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            # Decrypt
            decrypted_data = self.cipher.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None

# Global encryption service instance
encryption_service = EncryptionService()

def encrypt_mpesa_credential(credential):
    """Encrypt M-PESA credential"""
    return encryption_service.encrypt(credential)

def decrypt_mpesa_credential(encrypted_credential):
    """Decrypt M-PESA credential"""
    return encryption_service.decrypt(encrypted_credential)