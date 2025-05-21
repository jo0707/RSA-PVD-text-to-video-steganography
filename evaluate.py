import os
import shutil
import time
from colorama import Fore, Style
import cv2
import csv
import numpy as np
import src.pvd as pvd
import src.rsa as rsa
import src.video_parser as video_parser

FRAMES_DIR = os.path.join("input", "frames")
OUTPUT_DIR = 'output'
DURATIONS = [1, 5, 10, 15]
VIDEO_PATHS = [os.path.join('input', f'{duration}_video.mp4') for duration in DURATIONS]
OUTPUT_PATHS = [os.path.join(OUTPUT_DIR, f'{duration}_video.avi') for duration in DURATIONS]
MESSAGE = "This is a secret message."

input_encrpyted_messages = []
output_encrpyted_messages = []

def psnr():
    def calculate_psnr(before_path, after_path):
        image1 = cv2.imread(before_path)
        image2 = cv2.imread(after_path)
        mse = np.mean((image1 - image2) ** 2)
        if mse == 0:
            return float('inf')
        max_pixel = 255.0
        psnr_value = 20 * np.log10(max_pixel / np.sqrt(mse))
        return psnr_value
    
    before_path = os.path.join("psnr", "before.png")
    after_path = os.path.join("psnr", "after.png")
    psnr_value = calculate_psnr(before_path, after_path)
    
    # Save PSNR result to CSV
    csv_path = os.path.join("output", "evaluate_psnr_results.csv")
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Image1", "Image2", "PSNR"])
        writer.writerow([before_path, after_path, psnr_value])
    
    print(Fore.YELLOW + f"PSNR value calculated: {psnr_value}")

def evaluate_encrypt(video_path, message, output_video_path):
    video_parser.extract_frames(video_path, FRAMES_DIR)
    
    # remove directory if exists
    if os.path.exists("psnr"):
        shutil.rmtree("psnr")
    
    # copy the first frame to /psnr
    os.makedirs("psnr", exist_ok=True)
    os.makedirs(FRAMES_DIR, exist_ok=True)
    shutil.copy(os.path.join(FRAMES_DIR, "frame_00000.png"), os.path.join("psnr", "before.png"))
    
    encrypted_message = rsa.encrypt_message_base64(message)
    image_path = os.path.join(FRAMES_DIR, "frame_00000.png")
    bits, chars = pvd.check_pvd_capacity(image_path)
    pvd.embed_pvd(image_path, encrypted_message, image_path)
    input_encrpyted_messages.append(encrypted_message)
    
    # copy the stego frame to /psnr
    shutil.copy(os.path.join(FRAMES_DIR, "frame_00000.png"), os.path.join("psnr", "after.png"))
    psnr()
    
    video_parser.combine_frames_to_video(FRAMES_DIR, output_video_path)
    
    print(Fore.GREEN + Style.BRIGHT + "Kapasitas Max Bits: " + str(bits) + " | Chars: " + str(chars))
    print(Fore.CYAN + f"Pesan Terenkripsi: {encrypted_message}")
    print(Fore.GREEN + Style.BRIGHT + f"Pesan telah dienkripsi dan disisipkan ke dalam video {video_path}.")

def evaluate_decrypt(stego_video_path):
    if not stego_video_path:
        stego_video_path = "output_video.avi"
    
    # Extract frames from stego video
    video_parser.extract_frames(stego_video_path, FRAMES_DIR)
    
    try:
        # Extract and decrypt message from frames
        stego_image_path = os.path.join(FRAMES_DIR, "frame_00000.png")
        extracted_message = pvd.extract_pvd(stego_image_path)
        output_encrpyted_messages.append(extracted_message)
        print(Fore.CYAN + f"Pesan diekstrak (Terenkripsi): {extracted_message}")
        
        decrypted_message = rsa.decrypt_message_base64(extracted_message)
        print(Fore.GREEN + Style.BRIGHT + f"Pesan yang diekstrak dan didekripsi: {decrypted_message}")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")
        print(Fore.RED + "Pesan tidak dapat didekripsi. Kemungkinan pesan tidak valid atau rusak.")

if __name__ == "__main__":
        # remove /output/evaluate_psnr_results.csv if exists
    if os.path.exists("output/evaluate_psnr_results.csv"):
        os.remove("output/evaluate_psnr_results.csv")
    
    # Encrypt and decrypt videos
    for video_path, output_path in zip(VIDEO_PATHS, OUTPUT_PATHS):
        print(Fore.GREEN + f"--------------------------------")
        print(Fore.YELLOW + f"Processing video: {video_path}")
        evaluate_encrypt(video_path, MESSAGE, output_path)
        evaluate_decrypt(output_path)
    
    results = []
    for i, (input_msg, output_msg) in enumerate(zip(input_encrpyted_messages, output_encrpyted_messages)):
        print(Fore.YELLOW + f"Video {i+1}:")
        results.append(input_msg == output_msg)
        if input_msg == output_msg:
            print(Fore.GREEN + "Pesan terenkripsi sama.")
        else:
            print(Fore.RED + "Pesan terenkripsi berbeda.")
            
    success_rate = (sum(results) / len(results)) * 100
    print(Fore.GREEN + f"Keberhasilan enkripsi dan dekripsi: {success_rate:.2f}%")
    print(Fore.GREEN + f"--------------------------------")
    print(Fore.YELLOW + f"Evaluasi selesai.")
    
    if(os.path.exists("psnr")):
        shutil.rmtree("psnr")