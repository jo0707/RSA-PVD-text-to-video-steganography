import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
from colorama import init, Fore, Style

PRIVATE_KEY_PATH = os.path.join("keys", "private_key.pem")
PUBLIC_KEY_PATH = os.path.join("keys", "public_key.pem")

def generate_rsa_keys(key_size=2048):
    if not os.path.exists("keys"):
        os.makedirs("keys")
    if os.path.exists(PRIVATE_KEY_PATH) and os.path.exists(PUBLIC_KEY_PATH):
        print(Fore.YELLOW + Style.BRIGHT + "Kunci sudah dibuat! Hapus file kunci (/keys) untuk membuat yang baru.")
        return None, None
    
    key = RSA.generate(key_size)
    private_key = key.export_key().decode()
    public_key = key.publickey().export_key().decode()
    
    # Simpan kunci privat ke file
    with open(PRIVATE_KEY_PATH, "w") as private_file:
        private_file.write(private_key)
    with open(PUBLIC_KEY_PATH, "w") as public_file:
        public_file.write(public_key)
    
    return private_key, public_key

def encrypt_message_base64(message: str) -> str:
    """
    Enkripsi pesan menggunakan kunci publik RSA dan hasil base64.
    """
    with open(PUBLIC_KEY_PATH, "r") as public_file:
        public_key_pem = public_file.read()
        
    public_key = RSA.import_key(public_key_pem)
    cipher = PKCS1_OAEP.new(public_key)
    encrypted = cipher.encrypt(message.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_message_base64(encrypted_base64: str) -> str:
    """
    Dekripsi pesan base64 menggunakan kunci privat RSA.
    """
    with open(PRIVATE_KEY_PATH, "r") as private_file:
        private_key_pem = private_file.read()
    private_key = RSA.import_key(private_key_pem)
    cipher = PKCS1_OAEP.new(private_key)
    decrypted = cipher.decrypt(base64.b64decode(encrypted_base64))
    return decrypted.decode()
