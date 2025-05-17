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
def decrypt_message(ciphertext: str) -> str:
    if not os.path.exists("private_key.pem"):
        print("Private key not found. Returning original message.")
        return ciphertext
    
    # Load private key from file
    with open("private_key.pem", "rb") as priv_file:
        private_key_bytes = priv_file.read()
    
    try:
        # Clean the ciphertext - remove any non-base64 characters
        cleaned_ciphertext = ''.join(c for c in ciphertext if c in 
                                  'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
        
        # Check if the cleaned string is empty
        if not cleaned_ciphertext:
            raise ValueError("No valid base64 characters found in the input")
            
        # Make sure the length is valid for base64
        padding_needed = len(cleaned_ciphertext) % 4
        if padding_needed:
            cleaned_ciphertext += '=' * (4 - padding_needed)
            
        try:
            # Decode base64
            unbase64_ciphertext = base64.b64decode(cleaned_ciphertext)
            
            # RSA with PKCS1_OAEP has a specific length requirement based on key size
            # Try decrypting
            private_key = RSA.import_key(private_key_bytes)
            cipher_rsa = PKCS1_OAEP.new(private_key)
            decrypted = cipher_rsa.decrypt(unbase64_ciphertext)
            return decrypted.decode('utf-8', errors='replace')
        except ValueError as e:
            # This might happen if the base64 string is corrupted but still valid base64
            # Try to reconstruct from partial data
            if "incorrect length" in str(e):
                # Try to trim the data to match the expected length
                # Default RSA-2048 block size is 256 bytes
                key_size = RSA.import_key(private_key_bytes).size_in_bytes()
                if len(unbase64_ciphertext) > key_size:
                    # Try to use only the first block
                    print(f"Trying to recover from corrupted data (using first {key_size} bytes)...")
                    try:
                        private_key = RSA.import_key(private_key_bytes)
                        cipher_rsa = PKCS1_OAEP.new(private_key)
                        decrypted = cipher_rsa.decrypt(unbase64_ciphertext[:key_size])
                        return decrypted.decode('utf-8', errors='replace')
                    except:
                        # If that fails, try the original approach but with a warning
                        raise ValueError("Data is corrupted and cannot be decrypted")
                else:
                    raise ValueError("Data is too short for RSA decryption")
            else:
                raise
    except Exception as e:
        print(f"Decryption error: {e}")
        # If decryption fails, return a message
        return f"Unable to decrypt message: possibly corrupted data. Error: {str(e)}"

