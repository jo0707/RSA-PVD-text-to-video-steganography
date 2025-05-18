from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
from colorama import init, Fore, Style

def generate_rsa_keys(key_size=2048):
    """
    Menghasilkan pasangan kunci RSA.
    Return: (private_key_pem: str, public_key_pem: str)
    """
    import os
    if not os.path.exists("keys"):
        os.makedirs("keys")
    if os.path.exists("keys/private_key.pem") and os.path.exists("keys/public_key.pem"):
        print(Fore.YELLOW + Style.BRIGHT + "Kunci sudah dibuat! Hapus file kunci (/keys) untuk membuat yang baru.")
        return None, None
    
    key = RSA.generate(key_size)
    private_key = key.export_key().decode()
    public_key = key.publickey().export_key().decode()
    
    # Simpan kunci privat ke file
    with open("keys/private_key.pem", "w") as private_file:
        private_file.write(private_key)
    with open("keys/public_key.pem", "w") as public_file:
        public_file.write(public_key)
    
    return private_key, public_key

def encrypt_message_base64(message: str) -> str:
    """
    Enkripsi pesan menggunakan kunci publik RSA dan hasil base64.
    """
    with open("keys/public_key.pem", "r") as public_file:
        public_key_pem = public_file.read()
        
    public_key = RSA.import_key(public_key_pem)
    cipher = PKCS1_OAEP.new(public_key)
    encrypted = cipher.encrypt(message.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_message_base64(encrypted_base64: str) -> str:
    """
    Dekripsi pesan base64 menggunakan kunci privat RSA.
    """
    with open("keys/private_key.pem", "r") as private_file:
        private_key_pem = private_file.read()
    private_key = RSA.import_key(private_key_pem)
    cipher = PKCS1_OAEP.new(private_key)
    decrypted = cipher.decrypt(base64.b64decode(encrypted_base64))
    return decrypted.decode()
