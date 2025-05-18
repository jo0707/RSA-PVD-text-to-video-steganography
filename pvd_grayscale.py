from PIL import Image
import math

# Fungsi untuk menentukan range dan kapasitas bit
def get_range_and_bits(d):
    ranges = [(0, 7), (8, 15), (16, 31), (32, 63), (64, 127), (128, 255)]
    for (lower, upper) in ranges:
        if lower <= d <= upper:
            return (lower, upper, int(math.floor(math.log2(upper - lower + 1))))
    return (0, 0, 0)

# Fungsi menyisipkan pesan ke gambar
def embed_pvd_grayscale(image_path, message, output_path='stego.png'):
    img = Image.open(image_path)
    img = img.convert('L')  # konversi ke grayscale
    pixels = list(img.getdata())
    
    binary_msg = ''.join([format(ord(c), '08b') for c in message]) + '11111111'  # Terminator
    msg_index = 0
    
    for i in range(0, len(pixels)-1, 2):
        if msg_index >= len(binary_msg):
            print("Pesan sudah disisipkan sepenuhnya.")
            break

        p1, p2 = pixels[i], pixels[i+1]
        d = abs(p2 - p1)
        r_lower, _, bits = get_range_and_bits(d)
        if bits == 0:
            continue

        segment = binary_msg[msg_index:msg_index + bits]
        
        # padding must be in the end only
        if len(segment) < bits:
            segment += '0' * (bits - len(segment))

        msg_index += bits
        m = int(segment, 2)
        new_d = r_lower + m

        """
        Menghitung nilai piksel baru 
        p1_new dan p2_new
        sehingga selisihnya menjadi new_d
        namun tetap menjaga rata-rata (brightness) 
        dari p1 dan p2 agar citra tidak berubah drastis.

        p1_new = round((10 + 20 - 5) / 2) = round(25 / 2) = 12
        p2_new = 12 + 5 = 17
        """
        if p2 >= p1:
            p1_new = round((p1 + p2 - new_d) / 2)
            p2_new = p1_new + new_d
        else:
            p1_new = round((p1 + p2 + new_d) / 2)
            p2_new = p1_new - new_d
            
        if (p2_new > 254):
            print(f"p2_new > 254!")
            print(f"p1 = {p1} | p2 = {p2} | d = {d} | new_d = {new_d} | p1_new = {p1_new} | p2_new = {p2_new}")

        if (p1_new < 0):
            p2_new = p2_new + abs(p1_new)
            p1_new = 0
        elif (p2_new > 255):
            p1_new = p1_new - (p2_new - 255)
            p2_new = 255
            print(f"p1 = {p1} | p2 = {p2} | d = {d} | new_d = {new_d} | p1_new = {p1_new} | p2_new = {p2_new}")
            
        pixels[i] = p1_new
        pixels[i+1] = p2_new
            
    # Simpan gambar stego
    img.putdata(pixels)
    img.save(output_path)

# Fungsi ekstraksi pesan
def extract_pvd_grayscale(stego_path):
    img = Image.open(stego_path)
    img = img.convert('L')
    pixels = list(img.getdata())
    
    bits = ''
    for i in range(0, len(pixels)-1, 2):
        p1, p2 = pixels[i], pixels[i+1]
        d = abs(p2 - p1)
        _, _, nbits = get_range_and_bits(d)
        bits += format(d, f'0{nbits}b')

    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    message = ''
    messageBinary = ''
    for c in chars:
        if c == '11111111':  # Terminator (0x00)
            break
            
        messageBinary += c
        message += chr(int(c, 2))

    return message

def check_pvd_capacity_grayscale(image_path):
    """
    Menghitung kapasitas maksimum (dalam bit dan karakter) yang dapat disisipkan ke dalam gambar
    menggunakan algoritma PVD.
    """
    img = Image.open(image_path)
    img = img.convert('L')
    pixels = list(img.getdata())
    total_bits = 0
    for i in range(0, len(pixels)-1, 2):
        p1, p2 = pixels[i], pixels[i+1]
        d = abs(p2 - p1)
        _, _, bits = get_range_and_bits(d)
        total_bits += bits
    total_chars = total_bits // 8
    return total_bits, total_chars

if __name__ == "__main__":
    # Contoh penggunaan
    image_path = 'input_image.png'
    message = "Hello, this is a secret message!"
    output_path = 'stego_image.png'
    
    # Cek kapasitas gambar
    total_bits, total_chars = check_pvd_capacity_grayscale(image_path)    
    print(f"Kapasitas maksimum: {total_bits} bit ({total_chars} karakter)")
    
    embed_pvd_grayscale(image_path, message, output_path)
    print(f"Pesan '{message}' berhasil disisipkan ke dalam {output_path}")
    
    extracted_message = extract_pvd_grayscale(output_path)
    print(f"Pesan yang diekstrak: {extracted_message}")