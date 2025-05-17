import base64
import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes

# Fungsi untuk generate pasangan kunci RSA
def generate_rsa_keys(key_size=2048):
    key = RSA.generate(key_size)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    
    # Save keys to files (optional)
    with open("private_key.pem", "wb") as priv_file:
        priv_file.write(private_key)
    with open("public_key.pem", "wb") as pub_file:
        pub_file.write(public_key)
    
    return private_key, public_key

# Fungsi untuk enkripsi teks (dengan kunci publik)
def encrypt_message(message: str) -> bytes:
    # if no public key is found, return as is
    if not os.path.exists("public_key.pem"):
        print("Public key not found. Returning original message.")
        return message
    
    # Load public key from file
    with open("public_key.pem", "rb") as pub_file:
        public_key_bytes = pub_file.read()
        
    public_key = RSA.import_key(public_key_bytes)
    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted = cipher_rsa.encrypt(message.encode())
    
    # return encrypted as base64 string
    return base64.b64encode(encrypted).decode('utf-8')

# Fungsi untuk dekripsi teks terenkripsi (dengan kunci privat)
def decrypt_message(ciphertext: bytes) -> str:
    if not os.path.exists("private_key.pem"):
        print("Private key not found. Returning original message.")
        return ciphertext
    
    # Load private key from file
    with open("private_key.pem", "rb") as priv_file:
        private_key_bytes = priv_file.read()
    
    unbase64_ciphertext = base64.b64decode(ciphertext)
    
    private_key = RSA.import_key(private_key_bytes)
    cipher_rsa = PKCS1_OAEP.new(private_key)
    decrypted = cipher_rsa.decrypt(unbase64_ciphertext)
    return decrypted.decode()

