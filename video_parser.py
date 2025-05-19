import cv2
import os

def extract_frames(video_path = 'input_video.mp4', frames_dir = 'frames'):
    """
    Mengekstrak setiap frame dari video dan menyimpannya ke direktori output_dir.
    """
    if not os.path.exists(frames_dir):
        os.makedirs(frames_dir)
    
    # remove existing frames
    for f in os.listdir(frames_dir):
        os.remove(os.path.join(frames_dir, f))
    
    cap = cv2.VideoCapture(video_path)
    count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_path = os.path.join(frames_dir, f"frame_{count:05d}.png")
        cv2.imwrite(frame_path, frame)
        if count % 100 == 0:
            print(f"Ekstrak frame {count} ke {frame_path}")
        count += 1
    cap.release()
    print(f"{count} frames berhasil diekstrak ke {frames_dir}")

def combine_frames_to_video(frames_dir, output_video_path, fps=30):
    """
    Menggabungkan semua frame di frames_dir menjadi video lossless (AVI, FFV1 codec),
    sehingga data PVD tetap utuh dan bisa diekstrak kembali.
    """
    import cv2
    import os
    frames = sorted([f for f in os.listdir(frames_dir) if f.endswith('.png')])
    if not frames:
        print("Tidak ada frame ditemukan di direktori.")
        return
    first_frame = cv2.imread(os.path.join(frames_dir, frames[0]))
    height, width, layers = first_frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')  # Codec lossless
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    for frame_name in frames:
        frame = cv2.imread(os.path.join(frames_dir, frame_name))
        out.write(frame)
        if int(frame_name.split('_')[1].split('.')[0]) % 100 == 0:
            print(f"Menulis frame {frame_name} ke {output_video_path}")
    out.release()
    print(f"Video lossless berhasil dibuat: {output_video_path}")

# Contoh penggunaan
if __name__ == "__main__":
    video_path = 'input_video.mp4'
    frames_dir = 'frames'
    output_video_path = 'output_video.avi'
    fps = 30
    # Ekstrak frame
    extract_frames(video_path, frames_dir)
    # Gabungkan kembali menjadi video
    combine_frames_to_video(frames_dir, output_video_path, fps)

