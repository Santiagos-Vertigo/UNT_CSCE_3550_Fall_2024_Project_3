from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import base64

# Secret key for AES encryption (must be 16, 24, or 32 bytes long)
NOT_MY_KEY = os.getenv('NOT_MY_KEY', 'default_secret_key').encode()

def encrypt_data(data):
    """
    Encrypts the provided data using AES encryption.
    """
    iv = os.urandom(16)  # Generate a random initialization vector
    cipher = Cipher(algorithms.AES(NOT_MY_KEY), modes.CFB(iv))
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data.encode()) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_data).decode()

def decrypt_data(encrypted_data):
    """
    Decrypts the provided encrypted data using AES encryption.
    """
    encrypted_data = base64.b64decode(encrypted_data)
    iv = encrypted_data[:16]  # Extract the initialization vector
    cipher = Cipher(algorithms.AES(NOT_MY_KEY), modes.CFB(iv))
    decryptor = cipher.decryptor()
   
