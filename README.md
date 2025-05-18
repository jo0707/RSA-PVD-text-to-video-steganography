# RSA-PVD Text-to-Video Steganography

A Python implementation that combines RSA encryption with Pixel Value Differencing (PVD) steganography to securely hide text messages in image files.

## Overview

This project provides a secure method for hiding text messages in images using two main techniques:

1. **RSA Encryption**: The text is first encrypted using RSA asymmetric encryption, providing a strong layer of security.
2. **Pixel Value Differencing (PVD) Steganography**: The encrypted message is then embedded into an image using the PVD technique, which modifies pixel values based on their differences to store information while minimizing visual distortion.

## Features

-   Secure RSA key generation (2048-bit by default)
-   Text encryption using RSA with PKCS1_OAEP padding
-   High-capacity PVD steganography implementation
-   Automatic capacity calculation for images
-   Error handling and recovery mechanisms
-   Simple command-line interface

## Requirements

-   Python 3.7+
-   OpenCV (cv2)
-   NumPy
-   PyCryptodome

## Installation

1. Clone the repository:

```bash
git clone https://github.com/jo0707/RSA-PVD-text-to-video-steganography.git
cd RSA-PVD-text-to-video-steganography
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the main script:

```bash
python main.py
```

### Options

1. **Hide text in video**:

    - Takes text input and hides it in the specified image file
    - Automatically encrypts the text using RSA
    - Saves the resulting stego image

2. **Extract text from stego image**:

    - Extracts the hidden text from a stego image
    - Automatically decrypts the message if RSA private key is available

3. **Generate RSA keys (optional)**:
    - Generates RSA key pair (public and private keys)
    - Saves keys to disk for later use

## How It Works

### RSA Encryption

-   Uses asymmetric encryption where a public key encrypts data and a private key decrypts it
-   Implemented using the PyCryptodome library with PKCS1_OAEP padding
-   Keys are stored in PEM format in the same directory

### PVD Steganography

-   Divides the image into pixel pairs
-   Calculates the difference between adjacent pixels
-   Modifies these differences to embed message bits
-   Uses a special terminator pattern to mark the end of the message
-   Distributes the message across RGB channels for higher capacity

## Video Steganography Progress

This project now supports **video steganography using PVD** for selected frames:

-   Text is encrypted with RSA, then hidden in multiple video frames using the PVD method.
-   Frames are extracted from the video, the message is embedded in one or more frames, and the frames are recombined into a lossless video (AVI/FFV1 or MJPEG).
-   Extraction and decryption are supported for stego video.
-   Lossless processing ensures the PVD data is preserved and can be read back correctly.
-   Frame management and recombination are handled automatically.

**Note:** Only some frames are used for steganography, not the entire video. This increases security and reduces visual impact.

## Advanced Features

-   Automatic detection of message terminator
-   Smart error handling for corrupted data
-   Capacity estimation before embedding
-   Minimal visual impact on carrier images

## Example

```python
# Example: Hiding text
python main.py
# Select option 1, enter text
# Result: stego_image.png is created with hidden message

# Example: Extracting text
python main.py
# Select option 2
# Result: Extracted and decrypted message is displayed
```

## Notes

-   The steganography technique works best with lossless image formats like PNG
-   JPEG compression will likely destroy the hidden data
-   Using larger images provides more hiding capacity
-   RSA encryption is limited by key size (typically ~245 bytes of data per 2048-bit key)

## License

[MIT License](LICENSE)

## Contributors

-   [Your Name]

## Acknowledgments

-   This project is for educational purposes only
-   Based on the PVD steganography technique proposed by Da-Chun Wu and Wen-Hsiang Tsai
