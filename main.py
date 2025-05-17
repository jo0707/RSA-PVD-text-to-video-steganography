import pvd
import rsa

# Example usage
def main():
    pvd_stego = pvd.PVDSteganography()

    print("PVD Steganography Example")
    print("1. Hide text in image")
    print("2. Extract text from stego image")
    print("3. Generate RSA keys (optional)")
    choice = input("Enter your choice (1/2/3): ")

    if choice not in ['1', '2', '3']:
        print("Invalid choice. Exiting.") 
        return
    if choice == '1':
        # Hide text in image
        image_path = "original_image.png"
        output_path = "stego_image.png"

        input_text = input("Enter the secret text to hide: ")
        secret_text = input_text.encode('utf-8').decode('utf-8', 'ignore')

        if len(secret_text) == 0:
            print("No text provided. Exiting.")
            return
        if len(secret_text) > 1000:
            print("Text too long. Please provide a shorter message.")
            return

        secret_text = rsa.encrypt_message(secret_text)
        print("Encrypted text:", secret_text)
        print("Hiding text in image...")

        try:
            pvd_stego.hide_text(image_path, secret_text, output_path)
            print(f"Secret text hidden in {output_path}")
        except Exception as e:
            print(f"Error: {e}")

    elif choice == '2':
        # Extract text from stego image
        stego_path = "stego_image.png"

        try:
            extracted_text = pvd_stego.extract_text(stego_path)
            print("Extracted text:", extracted_text)

            decrypted_text = rsa.decrypt_message(extracted_text)
            print("Decrypted text:", decrypted_text)
        except Exception as e:
            print(f"Error: {e}")

    elif choice == '3':
        # Generate RSA keys
        priv_key, pub_key = rsa.generate_rsa_keys()
        print("Private Key:\n", priv_key.decode()[:300], "...")
        print("Public Key:\n", pub_key.decode()[:300], "...")

if __name__ == "__main__":
    main()
