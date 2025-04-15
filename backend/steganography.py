import numpy as np
from PIL import Image, UnidentifiedImageError
import os
import logging
from cryptography.fernet import Fernet
import base64
import hashlib

logging.basicConfig(level=logging.INFO)

def generate_key(password: str) -> bytes:
    """Generate encryption key from password"""
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

def encrypt_message(message: str, password: str) -> str:
    """Encrypt message using password"""
    if not password:
        return message
    return Fernet(generate_key(password)).encrypt(message.encode()).decode()

def decrypt_message(encrypted: str, password: str) -> str:
    """Decrypt message using password"""
    if not password:
        return encrypted
    return Fernet(generate_key(password)).decrypt(encrypted.encode()).decode()

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def save_temp_file(file) -> str:
    """Save uploaded file to temp directory"""
    filepath = os.path.join('temp', file.filename)
    file.save(filepath)
    return filepath

def lsb_encode(image_path: str, message: str, output_path: str, password: str = None) -> None:
    """Core LSB encoding logic"""
    try:
        img = np.array(Image.open(image_path))
        
        # Add prefix to indicate encryption status
        if password:
            encrypted_msg = encrypt_message(message, password)
            message_to_encode = f"ENC:{encrypted_msg}"
        else:
            message_to_encode = f"TXT:{message}"

        binary_msg = ''.join([format(ord(c), '08b') for c in message_to_encode + "%%%"])
        if len(binary_msg) > img.size:
            raise ValueError("Message too large for image")

        flat = img.flatten()
        for i in range(len(binary_msg)):
            flat[i] = (flat[i] & 0xFE) | int(binary_msg[i])

        Image.fromarray(flat.reshape(img.shape)).save(output_path)
    except Exception as e:
        logging.error(f"Encoding failed: {str(e)}")
        raise

def lsb_decode(image_path: str, password: str = None) -> str:
    """Core LSB decoding logic with proper decryption handling"""
    try:
        flat = np.array(Image.open(image_path)).flatten()
        binary = ''.join([str(pixel & 1) for pixel in flat])

        # Extract the message from LSB
        message = ""
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) < 8:
                break
            message += chr(int(byte, 2))
            if message.endswith("%%%"):
                message = message[:-3]  # Remove termination marker
                break

        # Handle different message types
        if message.startswith("ENC:"):
            if not password:
                raise ValueError("Password required for decoding this message.")
            encrypted_msg = message[4:]  # Remove 'ENC:' prefix
            try:
                return decrypt_message(encrypted_msg, password)
            except Exception as e:
                raise ValueError("Incorrect password or corrupted message")
        elif message.startswith("TXT:"):
            return message[4:]  # Remove 'TXT:' prefix
        else:
            # For backward compatibility with old format
            return message
    except Exception as e:
        logging.error(f"Decoding failed: {str(e)}")
        raise