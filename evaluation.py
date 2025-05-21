import time
import matplotlib.pyplot as plt
import numpy as np
from colorama import Fore
from main import decrypt_video, encrypt_video

# Daftar video uji coba dengan durasi berbeda
INPUT_VIDEO_PATHS = [
    "evaluation video/1s_video.mp4",
    "evaluation video/5s_video.mp4",
    "evaluation video/10_video.mp4",
    "evaluation video/15_.mp4"
]

# Output setelah enkripsi
OUTPUT_VIDEO_PATHS = [
    "evaluation video/1s_video.avi",
    "evaluation video/5s_video.avi",
    "evaluation video/10s_video.avi",
    "evaluation video/15s_video.avi"
]

MESSAGE = "Adakah nona ambon disini?"  
N_RUNS = 5 

def measure_time(func, *args):
    start_time = time.time()
    func(*args)
    return time.time() - start_time

def evaluate():
    encrypt_times_all = []
    decrypt_times_all = []

    for i in range(len(INPUT_VIDEO_PATHS)):
        print(Fore.CYAN + f"\n[INFO] Evaluasi video durasi ke-{i+1}: {INPUT_VIDEO_PATHS[i]}")
        encrypt_times = []
        decrypt_times = []

        for run in range(N_RUNS):
            print(Fore.YELLOW + f"  ↪ Run ke-{run+1}...")
            enc_time = measure_time(encrypt_video, INPUT_VIDEO_PATHS[i], MESSAGE, OUTPUT_VIDEO_PATHS[i])
            encrypt_times.append(enc_time)

            dec_time = measure_time(decrypt_video, OUTPUT_VIDEO_PATHS[i])
            decrypt_times.append(dec_time)

        encrypt_times_all.append(encrypt_times)
        decrypt_times_all.append(decrypt_times)

    return encrypt_times_all, decrypt_times_all

def plot_results(encrypt_times_all, decrypt_times_all):
    durations = ["1s", "5s", "10s", "15s"]
    x = np.arange(len(durations))

    # Hitung rata-rata dan standar deviasi
    enc_means = [np.mean(t) for t in encrypt_times_all]
    enc_stds = [np.std(t) for t in encrypt_times_all]
    dec_means = [np.mean(t) for t in decrypt_times_all]
    dec_stds = [np.std(t) for t in decrypt_times_all]

    width = 0.35

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, enc_means, width, yerr=enc_stds, label='Encryption Time', color='royalblue', capsize=5)
    rects2 = ax.bar(x + width/2, dec_means, width, yerr=dec_stds, label='Decryption Time', color='darkorange', capsize=5)

    ax.set_ylabel('Time (seconds)')
    ax.set_xlabel('Video Duration')
    ax.set_title('Average Encryption and Decryption Times\n(with Standard Deviation)')
    ax.set_xticks(x)
    ax.set_xticklabels(durations)
    ax.legend()
    ax.set_ylim(0, max(max(enc_means) + max(enc_stds), max(dec_means) + max(dec_stds)) + 0.3)

    # Tambahkan label angka
    def autolabel(rects, values):
        for rect, val in zip(rects, values):
            height = rect.get_height()
            ax.annotate(f'{val:.4f}s',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 5),  # offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)

    autolabel(rects1, enc_means)
    autolabel(rects2, dec_means)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    enc_times, dec_times = evaluate()
    plot_results(enc_times, dec_times)
