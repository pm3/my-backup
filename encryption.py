import base64
from typing import Dict
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
import os
import hashlib

BLOCK_SIZE = 16
CHUNK_SIZE = 16 * 1024  # násobok 16

def decrypt_key(key_row: Dict, password: str) -> bytes:
    # ===== Load data =====
    salt = base64.b64decode(key_row["salt"])
    nonce = base64.b64decode(key_row["nonce"])
    ciphertext = base64.b64decode(key_row["ciphertext"])

    # ===== Derive key from password again =====
    password_key = derive_password_key(password, salt)

    # ===== Decrypt AES key =====
    aesgcm = AESGCM(password_key)
    aes_key = aesgcm.decrypt(nonce, ciphertext, None)        
    return aes_key

def encrypt_key(aes_key: bytes, password: str) -> Dict:
    # ===== STEP 1: Derive key from password using PBKDF2 =====
    salt = os.urandom(16)  # random salt (store with cipher)
    password_key = derive_password_key(password, salt)

    # ===== STEP 2: Encrypt AES key using AES-GCM and password_key =====
    aesgcm = AESGCM(password_key)
    nonce = os.urandom(12)  # GCM nonce

    encrypted_aes_key = aesgcm.encrypt(nonce, aes_key, None)

    # Result: encoded AES key (store with salt and nonce)
    key_row = {
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(encrypted_aes_key).decode(),
    }
    return key_row

def derive_password_key(password: str, salt: bytes) -> bytes:
    """Derive a key from password using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=10_000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encrypt_stream(input_stream, key: bytes):
    """Šifruje vstupný stream pomocou AES-256-CBC. Vracia generator šifrovaných chunkov (IV + ciphertext)."""
    iv = os.urandom(BLOCK_SIZE)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()

    yield iv  # začni IV prefixom

    while chunk := input_stream.read(CHUNK_SIZE):
        padded = padder.update(chunk)
        if padded:
            yield encryptor.update(padded)

    # Zvyšné padding + finálny AES blok
    final_padded = padder.finalize()
    yield encryptor.update(final_padded) + encryptor.finalize()


def decrypt_stream_to_file(input_stream, filepath: str, key: bytes):
    """Dešifruje AES-256-CBC šifrovaný stream a uloží výsledok do súboru."""
    iv = input_stream.read(BLOCK_SIZE)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(128).unpadder()

    buffer = b""
    with open(filepath, "wb") as f_out:
        while True:
            chunk = input_stream.read(CHUNK_SIZE)
            if not chunk:
                break

            buffer += chunk
            while len(buffer) >= 32:
                block, buffer = buffer[:16], buffer[16:]
                decrypted = decryptor.update(block)
                f_out.write(unpadder.update(decrypted))

        # finálne bloky + unpadding
        decrypted = decryptor.update(buffer) + decryptor.finalize()
        unpadded = unpadder.update(decrypted) + unpadder.finalize()
        f_out.write(unpadded)

def calculate_file_hash(filepath: str) -> str:
    """Calculate SHA-256 hash of a file using streaming."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
