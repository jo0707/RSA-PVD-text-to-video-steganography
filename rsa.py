import binascii
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
    
    with open("private_key.pem", "wb") as priv_file:
        priv_file.write(private_key)
    with open("public_key.pem", "wb") as pub_file:
        pub_file.write(public_key)
    
    return private_key, public_key

def encrypt_message(message: str) -> str:
    if not os.path.exists("public_key.pem"):
        print("Public key not found. Returning original message.")
        return message
    
    # Load public key from file
    with open("public_key.pem", "rb") as pub_file:
        public_key_bytes = pub_file.read()
        
    public_key = RSA.import_key(public_key_bytes)
    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted = cipher_rsa.encrypt(message.encode())
    
    # Convert encrypted data to hexadecimal string instead of base64
    hex_str = binascii.hexlify(encrypted).decode('ascii')
    return hex_str

# Fungsi untuk dekripsi teks terenkripsi (dengan kunci privat)
def decrypt_message(ciphertext: str) -> str:
    if not os.path.exists("private_key.pem"):
        print("Private key not found. Returning original message.")
        return ciphertext
    
    # Early check for minimum length requirement
    if not ciphertext or len(ciphertext) < 10:
        print("Warning: Input data is too short to be an encrypted message")
        return "The extracted data is not a valid encrypted message or is corrupted"
    
    # Load private key from file
    with open("private_key.pem", "rb") as priv_file:
        private_key_bytes = priv_file.read()
    
    try:
        # Clean the ciphertext - remove any non-hex characters
        cleaned_ciphertext = ''.join(c for c in ciphertext if c in 
                                  '0123456789abcdefABCDEF')
        
        # Check if the cleaned string is empty or too short
        if not cleaned_ciphertext:
            raise ValueError("No valid hex characters found in the input")
        
        # Calculate expected length based on key size
        private_key = RSA.import_key(private_key_bytes)
        key_size_bytes = private_key.size_in_bytes()
        min_expected_hex_length = key_size_bytes * 2  # Each byte is 2 hex chars
        
        if len(cleaned_ciphertext) < min_expected_hex_length:
            print(f"Warning: Hex data too short ({len(cleaned_ciphertext)} chars), expected at least {min_expected_hex_length} chars")
            # If it's significantly shorter, likely not an encrypted message
            if len(cleaned_ciphertext) < min_expected_hex_length // 2:
                # Try to interpret as plain text if short
                if all(32 <= int(cleaned_ciphertext[i:i+2], 16) <= 126 for i in range(0, len(cleaned_ciphertext), 2) if i+1 < len(cleaned_ciphertext)):
                    print("Data may be plain text rather than encrypted")
                    # Try to convert hex to ASCII if it looks like ASCII
                    try:
                        if len(cleaned_ciphertext) % 2 != 0:
                            cleaned_ciphertext = '0' + cleaned_ciphertext
                        possible_text = bytes.fromhex(cleaned_ciphertext).decode('ascii', errors='replace')
                        return possible_text
                    except:
                        pass
                return f"The extracted data is too short to be a valid RSA encrypted message (got {len(cleaned_ciphertext)//2} bytes, need {key_size_bytes} bytes)"

        # Ensure length is even for proper hex decoding
        if len(cleaned_ciphertext) % 2 != 0:
            cleaned_ciphertext = '0' + cleaned_ciphertext
            
        try:
            # Decode hex string
            binary_data = binascii.unhexlify(cleaned_ciphertext)
            
            # Pad if needed
            if len(binary_data) < key_size_bytes:
                # Pad with zeros to match the expected RSA block size
                binary_data = binary_data.ljust(key_size_bytes, b'\0')
                print(f"Warning: Data was padded to match RSA block size ({key_size_bytes} bytes)")
            
            # Try decrypting
            cipher_rsa = PKCS1_OAEP.new(private_key)
            try:
                decrypted = cipher_rsa.decrypt(binary_data)
                return decrypted.decode('utf-8', errors='replace')
            except ValueError as e:
                if "Ciphertext with incorrect length" in str(e) and len(binary_data) > key_size_bytes:
                    # Try trimming to exactly one block
                    print(f"Trying with first block of data only...")
                    trimmed_data = binary_data[:key_size_bytes]
                    try:
                        decrypted = cipher_rsa.decrypt(trimmed_data)
                        return decrypted.decode('utf-8', errors='replace')
                    except:
                        raise ValueError(f"Unable to decrypt with first {key_size_bytes} bytes of data")
                raise
        except Exception as e:
            print(f"Hex decoding or RSA decryption error: {e}")
            raise
    except Exception as e:
        print(f"Decryption error: {e}")
        # If decryption fails, return a message
        return f"Unable to decrypt message: possibly corrupted data. Error: {str(e)}"

