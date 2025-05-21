from colorama import init, Fore, Style
import os

import src.pvd as pvd
import src.rsa as rsa
import src.video_parser as video_parser

# Colorama initialization
init(autoreset=True)

IMAGE_PATH = os.path.join("input", "original_image.png")
VIDEO_PATH = os.path.join("input", "original_video.mp4")
OUTPUT_IMAGE_PATH = os.path.join("output", "output_image.png")
OUTPUT_VIDEO_PATH = os.path.join("output", "output_video.avi")
FRAMES_DIR = os.path.join("input", "frames")
OUTPUT_FRAMES_DIR = os.path.join("output", "frames")

def encrypt_video(video_path, message, output_video_path):
    # Extract frames from video
    video_parser.extract_frames(video_path, FRAMES_DIR)
    
    # Encrypt message and embed it into frames
    encrypted_message = rsa.encrypt_message_base64(message)
    image_path = os.path.join(FRAMES_DIR, "frame_00000.png")
    pvd.embed_pvd(image_path, encrypted_message, image_path)
    
    # Combine frames back to video
    video_parser.combine_frames_to_video(FRAMES_DIR, output_video_path)
    print(Fore.GREEN + Style.BRIGHT + "Pesan telah dienkripsi dan disisipkan ke dalam video.")
    print(Fore.YELLOW + "Pastikan pengiriman video tidak terkompresi.")
    print(Fore.CYAN + f"Pesan Terenkripsi: {encrypted_message}")

def decrypt_video(stego_video_path):
    # Extract frames from stego video
    video_parser.extract_frames(stego_video_path, OUTPUT_FRAMES_DIR)
    
    # Extract and decrypt message from frames
    stego_image_path = os.path.join(OUTPUT_FRAMES_DIR, "frame_00000.png")
    extracted_message = pvd.extract_pvd(stego_image_path)
    print(Fore.CYAN + f"Pesan diekstrak (Terenkripsi): {extracted_message}")
    decrypted_message = rsa.decrypt_message_base64(extracted_message)
    print(Fore.GREEN + Style.BRIGHT + f"Pesan yang diekstrak dan didekripsi: {decrypted_message}")
    
    return decrypted_message

def encrypt_image(image_path, message, output_image_path):
    if not os.path.exists(image_path):
        print(Fore.RED + Style.BRIGHT + f"File gambar tidak ditemukan: {image_path}")
        return
    
    encrypted_message = rsa.encrypt_message_base64(message)
    pvd.embed_pvd(image_path, encrypted_message, output_image_path)
    print(Fore.GREEN + Style.BRIGHT + "Pesan telah dienkripsi dan disisipkan ke dalam gambar.")
    print(Fore.CYAN + f"Pesan: {encrypted_message}")
            
def decrypt_image(stego_image_path):
    extracted_message = pvd.extract_pvd(stego_image_path)
    decrypted_message = rsa.decrypt_message_base64(extracted_message)
    print(Fore.GREEN + Style.BRIGHT + f"Pesan yang diekstrak dan didekripsi: {decrypted_message}")

def main():
    rsa.generate_rsa_keys()
    
    while True:
        print(Fore.CYAN + Style.BRIGHT + "\n=== Steganografi Video PVD dengan RSA ===")
        choice = input(Fore.CYAN + Style.BRIGHT + """
Pilih opsi:
1. Enkripsi & Steganografi Video
2. Dekripsi & Desteganografi Video
3. Enkripsi & Steganografi Gambar
4. Dekripsi & Desteganografi Gambar
5. Keluar
Pilihan:
            """)
        if choice == '1':
            video_path = input(Fore.YELLOW + "Masukkan path video asli (original_video.mp4): ") or VIDEO_PATH
            message = input(Fore.YELLOW + "Masukkan pesan yang ingin disisipkan: ") or "Pesan rahasia"
            encrypt_video(video_path, message, OUTPUT_VIDEO_PATH) 
        elif choice == '2':
            stego_video_path = input(Fore.YELLOW + "Masukkan path video stego (output_video.avi): ") or OUTPUT_VIDEO_PATH
            decrypt_video(stego_video_path)
        if choice == '3':
            image_path = input(Fore.YELLOW + "Masukkan path gambar asli (original_image.png): ") or IMAGE_PATH
            output_image_path = input(Fore.YELLOW + "Masukkan path gambar output (output_image.png): ") or OUTPUT_IMAGE_PATH
            message = input(Fore.YELLOW + "Masukkan pesan yang ingin disisipkan: ") or "Pesan rahasia"
            encrypt_image(image_path, message, image_path, output_image_path)
        elif choice == '4':
            stego_image_path = input(Fore.YELLOW + "Masukkan path gambar stego (output_image.png): ") or OUTPUT_IMAGE_PATH
            decrypt_image(stego_image_path)
        elif choice == '5':
            print(Fore.MAGENTA + Style.BRIGHT + "Keluar dari program.") 
            break

if __name__ == "__main__":
    main()