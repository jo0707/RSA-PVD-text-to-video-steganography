import os

# File paths
INPUT_DIR = "input"
OUTPUT_DIR = "output"
FRAMES_DIR = os.path.join(INPUT_DIR, "frames")
OUTPUT_FRAMES_DIR = os.path.join(OUTPUT_DIR, "frames")
IMAGE_PATH = os.path.join(INPUT_DIR, "original_image.png")
VIDEO_PATH = os.path.join(INPUT_DIR, "original_video.mp4")
OUTPUT_IMAGE_PATH = os.path.join(OUTPUT_DIR, "output_image.png")
OUTPUT_VIDEO_PATH = os.path.join(OUTPUT_DIR, "output_video.avi")

# Style constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 400
PADDING = 20
BUTTON_HEIGHT = 40
PRIMARY_COLOR = "#2196F3"
SECONDARY_COLOR = "#757575"
BACKGROUND_COLOR = "#FFFFFF"
ERROR_COLOR = "#F44336"
SUCCESS_COLOR = "#4CAF50"