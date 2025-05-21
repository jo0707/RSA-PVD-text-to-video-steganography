import time
from colorama import Fore
from main import OUTPUT_VIDEO_PATH, decrypt_video, encrypt_video

def evaluate_time_encrypt():
    
    start_time = time.time()
    
    video_path = input(Fore.YELLOW + "Masukkan path video asli (original_video.mp4): ")
    message = input(Fore.YELLOW + "Masukkan pesan yang ingin disisipkan: ")
   
    encrypt_video(video_path, message,  OUTPUT_VIDEO_PATH)
    end_time = time.time()
    elapsed_time = end_time - start_time
    return elapsed_time

def evaluate_time_decrypt():
    
    start_time = time.time()
    
    stego_video_path = input(Fore.YELLOW + "Masukkan path video stego (output_video.avi): ")
   
    decrypt_video(stego_video_path)
    end_time = time.time()
    elapsed_time = end_time - start_time
    return elapsed_time

elapsed_time_encrypt = evaluate_time_encrypt()
elapsed_time_decrypt = evaluate_time_decrypt()

print (f"Waktu enkripsi = {elapsed_time_encrypt}")
print (f"Waktu dekripsi = {elapsed_time_decrypt}")