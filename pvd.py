import cv2
import numpy as np
import math

class PVDSteganography:
    def __init__(self):
        # Define ranges for pixel difference
        self.ranges = [
            (0, 7),      # R1
            (8, 15),     # R2
            (16, 31),    # R3
            (32, 63),    # R4
            (64, 127),   # R5
            (128, 255)   # R6
        ]
        
    def _get_range_index(self, diff):
        """Find which range the difference belongs to."""
        for i, (lower, upper) in enumerate(self.ranges):
            if lower <= diff <= upper:
                return i
        return len(self.ranges) - 1
    
    def _get_capacity(self, diff):
        """Calculate how many bits can be embedded in this pixel pair."""
        range_idx = self._get_range_index(diff)
        lower, upper = self.ranges[range_idx]
        return int(math.log2(upper - lower + 1))
    
    def _text_to_bits(self, text):
        """Convert text to a bit sequence."""
        bits = []
        # For each character, convert to 8 bits
        for char in text:
            ascii_val = ord(char)
            for i in range(7, -1, -1):  # 8 bits for each character
                bits.append((ascii_val >> i) & 1)
        
        # Add terminator sequence - special pattern that's unlikely to appear naturally
        terminator = [0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        for bit in terminator:
            bits.append(bit)
        return bits
    
    def _bits_to_text(self, bits):
        """Convert bit sequence back to text."""
        text = ""
        # Look for terminator pattern
        terminator_pattern = [0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        
        # Process bits in 8-bit chunks
        i = 0
        while i <= len(bits) - 8:
            # Check if we've reached the terminator
            if i <= len(bits) - 16 and bits[i:i+16] == terminator_pattern:
                break
                
            # Process an 8-bit character
            val = 0
            for j in range(8):
                if i + j < len(bits):
                    val = (val << 1) | bits[i + j]
                
            text += chr(val)
            i += 8
            
        return text
    
    def calculate_capacity(self, image_path):
        """Calculate the maximum capacity of the image in bits and bytes."""
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Could not load image: {image_path}")
        
        total_bits = 0
        total_pairs = 0
        
        # Process each color channel
        for channel in range(3):  # RGB channels
            height, width = img.shape[0], img.shape[1]
            row = 0
            
            while row < height - 1:
                col = 0
                while col < width - 1:
                    # Get pixel pair
                    p1 = int(img[row, col, channel])
                    p2 = int(img[row, col+1, channel])
                    
                    # Calculate difference
                    diff = abs(p1 - p2)
                    
                    # Calculate capacity
                    capacity = self._get_capacity(diff)
                    total_bits += capacity
                    total_pairs += 1
                    
                    col += 2  # Move to next pixel pair
                row += 1  # Move to next row
        
        # Calculate bytes (8 bits per byte)
        # Subtract 1 byte for terminator sequence
        total_bytes = (total_bits - 8) // 8
        
        # Characters (assuming 1 byte per character in ASCII)
        total_chars = total_bytes
        
        return {
            'bits': total_bits,
            'bytes': total_bytes,
            'characters': total_chars,
            'pixel_pairs': total_pairs
        }
    
    def hide_text(self, image_path, text, output_path):
        """Hide text in image using PVD method."""
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Could not load image: {image_path}")
        
        # Check capacity before hiding
        capacity = self.calculate_capacity(image_path)
        text_length = len(text)
        
        # Print capacity information
        print(f"Image capacity: {capacity['bytes']} bytes ({capacity['characters']} characters)")
        print(f"Text length: {text_length} characters ({text_length} bytes)")
        
        if text_length > capacity['characters']:
            print(f"Warning: Text is larger than the image capacity.")
            print(f"Only {capacity['characters']} out of {text_length} characters may be embedded.")
        
        # Make a copy of the image
        stego_img = img.copy()
        
        # Convert text to bits
        bits = self._text_to_bits(text)
        bit_index = 0
        total_bits = len(bits)
        
        # Process each color channel
        for channel in range(3):  # RGB channels
            height, width = img.shape[0], img.shape[1]
            row = 0
            
            while row < height - 1 and bit_index < total_bits:
                col = 0
                while col < width - 1 and bit_index < total_bits:
                    # Get pixel pairs - working with 2x2 blocks
                    p1 = int(img[row, col, channel])
                    p2 = int(img[row, col+1, channel])
                    
                    # Calculate difference
                    diff = abs(p1 - p2)
                    
                    # Find which range the difference belongs to
                    range_idx = self._get_range_index(diff)
                    lower, upper = self.ranges[range_idx]
                    
                    # Calculate capacity (number of bits we can hide)
                    capacity = self._get_capacity(diff)
                    
                    if capacity > 0 and bit_index < total_bits:
                        # Get bits to hide
                        bits_to_hide = 0
                        for i in range(min(capacity, total_bits - bit_index)):
                            bits_to_hide = (bits_to_hide << 1) | bits[bit_index]
                            bit_index += 1
                        
                        # Calculate new difference
                        new_diff = lower + bits_to_hide
                        
                        # Adjust pixels based on new difference
                        if p1 >= p2:
                            p1_new = p1 + math.ceil((new_diff - diff) / 2)
                            p2_new = p2 - math.floor((new_diff - diff) / 2)
                        else:
                            p1_new = p1 - math.ceil((new_diff - diff) / 2)
                            p2_new = p2 + math.floor((new_diff - diff) / 2)
                        
                        # Ensure values are within valid range
                        p1_new = max(0, min(255, p1_new))
                        p2_new = max(0, min(255, p2_new))
                        
                        # Update stego image
                        stego_img[row, col, channel] = p1_new
                        stego_img[row, col+1, channel] = p2_new
                    
                    col += 2  # Move to next pixel pair
                row += 1  # Move to next row
        
        # Check if all bits were embedded
        embedded_bytes = bit_index // 8
        total_bytes = total_bits // 8
        
        if bit_index < total_bits:
            print(f"Warning: Only {embedded_bytes} bytes out of {total_bytes} bytes were embedded.")
            print(f"This means {embedded_bytes - 1} characters out of {total_bytes - 1} characters were hidden.")
        else:
            print(f"All {text_length} characters ({total_bytes} bytes) were successfully hidden.")
        
        # Save stego image
        cv2.imwrite(output_path, stego_img)
        return stego_img
    
    def extract_text(self, stego_path):
        """Extract hidden text from a stego image."""
        # Load stego image
        stego_img = cv2.imread(stego_path)
        if stego_img is None:
            raise FileNotFoundError(f"Could not load image: {stego_path}")
        
        extracted_bits = []
        terminator_pattern = [0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        
        # Process each color channel
        for channel in range(3):
            height, width = stego_img.shape[0], stego_img.shape[1]
            row = 0
            
            # Check for terminator
            found_terminator = False
            
            while row < height - 1 and not found_terminator:
                col = 0
                while col < width - 1 and not found_terminator:
                    # Get pixel pairs
                    p1 = int(stego_img[row, col, channel])
                    p2 = int(stego_img[row, col+1, channel])
                    
                    # Calculate difference
                    diff = abs(p1 - p2)
                    
                    # Find which range the difference belongs to
                    range_idx = self._get_range_index(diff)
                    lower, upper = self.ranges[range_idx]
                    
                    # Calculate capacity
                    capacity = self._get_capacity(diff)
                    
                    if capacity > 0:
                        # Extract bits
                        value = diff - lower
                        for i in range(capacity - 1, -1, -1):
                            bit = (value >> i) & 1
                            extracted_bits.append(bit)
                            
                            # Check for terminator pattern
                            if len(extracted_bits) >= 16:
                                last_16_bits = extracted_bits[-16:]
                                if last_16_bits == terminator_pattern:
                                    # Remove the terminator pattern from the extracted bits
                                    extracted_bits = extracted_bits[:-16]
                                    found_terminator = True
                                    break
                    
                    col += 2  # Move to next pixel pair
                row += 1  # Move to next row
                
                if found_terminator:
                    break
            
            if found_terminator:
                break
        
        # Calculate and display extraction statistics
        extracted_bytes = len(extracted_bits) // 8
        
        print(f"Extracted data: {extracted_bytes} characters ({extracted_bytes} bytes)")
        
        # Convert extracted bits to text
        return self._bits_to_text(extracted_bits)


# Example usage
if __name__ == "__main__":
    pvd = PVDSteganography()
    
    image_path = input("Enter image path: ")
    try:
        # Calculate and show capacity
        capacity = pvd.calculate_capacity(image_path)
        print(f"Image capacity:")
        print(f"- Maximum capacity: {capacity['bits']} bits")
        print(f"- Available for data: {capacity['bytes']} bytes")
        print(f"- Can store approximately {capacity['characters']} ASCII characters")
    except Exception as e:
        print(f"Error: {e}")