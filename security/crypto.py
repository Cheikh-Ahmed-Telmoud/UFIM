import base64
from django.conf import settings
from cryptography.fernet import Fernet

def get_fernet_cipher():
    key = settings.UFIM_ENCRYPTION_KEY
    # Fernet key needs to be exactly 32 urlsafe base64-encoded bytes.
    # We ensure it's in bytes format.
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)

def encrypt_value(plain_text: str) -> str:
    if not plain_text:
        return ""
    cipher = get_fernet_cipher()
    encrypted_bytes = cipher.encrypt(plain_text.encode())
    return encrypted_bytes.decode()

def decrypt_value(encrypted_text: str) -> str:
    if not encrypted_text:
        return ""
    cipher = get_fernet_cipher()
    decrypted_bytes = cipher.decrypt(encrypted_text.encode())
    return decrypted_bytes.decode()
