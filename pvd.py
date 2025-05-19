from PIL import Image
import math

# Fungsi untuk menentukan range dan kapasitas bit
def get_range_and_bits(d):
    ranges = [(0, 7), (8, 15), (16, 31), (32, 63), (64, 127), (128, 255)]
    for (lower, upper) in ranges:
        if lower <= d <= upper:
            return (lower, upper, int(math.floor(math.log2(upper - lower + 1))))
    return (0, 0, 0)

# Fungsi untuk menyisipkan pesan ke gambar RGB
def embed_pvd(image_path, message, output_path='stego_rgb.png'):
    img = Image.open(image_path).convert('RGB')
    pixels = list(img.getdata())

    binary_msg = ''.join([format(ord(c), '08b') for c in message]) + '11111111'  # Terminator
    msg_index = 0

    new_pixels = []

    for i in range(0, len(pixels)-1, 2):
        if msg_index >= len(binary_msg):
            new_pixels.extend(pixels[i:])
            break

        p1 = list(pixels[i])
        p2 = list(pixels[i+1])

        for channel in range(3):  # R, G, B
            if msg_index >= len(binary_msg):
                break

            d = abs(p2[channel] - p1[channel])
            r_lower, _, bits = get_range_and_bits(d)
            if bits == 0:
                continue

            segment = binary_msg[msg_index: msg_index + bits]
            if len(segment) < bits:
                segment += '0' * (bits - len(segment))

            msg_index += bits
            m = int(segment, 2)
            new_d = r_lower + m

            if p2[channel] >= p1[channel]:
                p1_new = round((p1[channel] + p2[channel] - new_d) / 2)
                p2_new = p1_new + new_d
            else:
                p1_new = round((p1[channel] + p2[channel] + new_d) / 2)
                p2_new = p1_new - new_d

            # Validasi batas
            if p1_new < 0:
                p2_new += abs(p1_new)
                p1_new = 0
            elif p2_new > 255:
                p1_new -= (p2_new - 255)
                p2_new = 255

            p1[channel] = max(0, min(255, p1_new))
            p2[channel] = max(0, min(255, p2_new))

        new_pixels.append(tuple(p1))
        new_pixels.append(tuple(p2))

    img.putdata(new_pixels)
    img.save(output_path)

# Fungsi untuk mengekstrak pesan dari gambar RGB
def extract_pvd(stego_path):
    print("Ekstraksi pesan dari gambar...")
    img = Image.open(stego_path).convert('RGB')
    pixels = list(img.getdata())
    print(f"Jumlah pixel: {len(pixels)}")

    bits = ''
    for i in range(0, len(pixels)-1, 2):
        p1 = pixels[i]
        p2 = pixels[i+1]

        for channel in range(3):
            d = abs(p2[channel] - p1[channel])
            r_lower, _, nbits = get_range_and_bits(d)
            if nbits > 0:
                m = d - r_lower
                bits += format(m, f'0{nbits}b')

    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    message = ''
    for c in chars:
        if c == '11111111':
            break
        message += chr(int(c, 2))
    return message

# Cek kapasitas maksimum RGB
def check_pvd_capacity(image_path):
    img = Image.open(image_path).convert('RGB')
    pixels = list(img.getdata())
    total_bits = 0
    for i in range(0, len(pixels)-1, 2):
        p1, p2 = pixels[i], pixels[i+1]
        for channel in range(3):
            d = abs(p2[channel] - p1[channel])
            _, _, bits = get_range_and_bits(d)
            total_bits += bits
    total_chars = total_bits // 8
    return total_bits, total_chars

# Example usage
if __name__ == "__main__":
    image_path = 'original_image_320x210.png'
    output_path = 'output_image.png'
    message = "Pesan rahasia di gambar RGB"

    total_bits, total_chars = check_pvd_capacity(image_path)
    print(f"Kapasitas: {total_bits} bit ({total_chars} karakter)")

    embed_pvd(image_path, message, output_path)
    print("Pesan berhasil disisipkan!")

    extracted = extract_pvd(output_path)
    print(f"Pesan hasil ekstraksi: {extracted}")
    print("Pesan sama: ", message == extracted)
