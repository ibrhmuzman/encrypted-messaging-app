from PIL import Image
import io

from PIL import Image
import io

def stegano_embed(image_bytes: bytes, secret_text: str) -> bytes:
    # Key'i byte'a çevir
    key_bytes = secret_text.encode("utf-8")
    key_length = len(key_bytes)

    if key_length > 255:
        raise ValueError("Key 255 byte'tan büyük olamaz.")

    # Gömülecek veri: [1 byte length] + key bytes
    data = bytes([key_length]) + key_bytes
    bits = ''.join(f'{byte:08b}' for byte in data)

    # Resmi aç
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert("RGB")
    pixels = img.load()

    width, height = img.size
    total_pixels = width * height

    if len(bits) > total_pixels * 3:
        raise ValueError("Mesaj resmi gömmek için çok büyük!")

    bit_index = 0

    # Her pikselin R, G, B bitlerini LSB ile değiştir
    for y in range(height):
        for x in range(width):
            if bit_index >= len(bits):
                break

            r, g, b = pixels[x, y]

            # R kanalı
            if bit_index < len(bits):
                r = (r & 0xFE) | int(bits[bit_index])
                bit_index += 1

            # G kanalı
            if bit_index < len(bits):
                g = (g & 0xFE) | int(bits[bit_index])
                bit_index += 1

            # B kanalı
            if bit_index < len(bits):
                b = (b & 0xFE) | int(bits[bit_index])
                bit_index += 1

            pixels[x, y] = (r, g, b)

        if bit_index >= len(bits):
            break

    # PNG olarak kaydet
    output = io.BytesIO()
    img.save(output, format="PNG")
    return output.getvalue()


def stegano_extract(image_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert("RGB")
    pixels = img.load()

    width, height = img.size

    # ----- 1) Önce ilk 8 bit: key_length -----
    bits = ""
    bit_count = 0
    px = 0
    py = 0
    channel_index = 0  # 0: R, 1: G, 2: B

    # İlk 8 bit için
    while bit_count < 8:
        r, g, b = pixels[px, py]
        channels = [r, g, b]

        bits += str(channels[channel_index] & 1)
        bit_count += 1

        channel_index += 1
        if channel_index == 3:  # sonraki piksele geç
            channel_index = 0
            px += 1
            if px == width:
                px = 0
                py += 1

    key_length = int(bits, 2)

    # ----- 2) Şimdi key_length * 8 bit okuyacağız -----
    bits = ""
    bit_count = 0
    needed_bits = key_length * 8

    while bit_count < needed_bits:
        r, g, b = pixels[px, py]
        channels = [r, g, b]

        bits += str(channels[channel_index] & 1)
        bit_count += 1

        channel_index += 1
        if channel_index == 3:
            channel_index = 0
            px += 1
            if px == width:
                px = 0
                py += 1

    # ----- 3) Byte'lara çevir -----
    key_bytes = bytes(int(bits[i:i+8], 2) for i in range(0, needed_bits, 8))
    return key_bytes.decode("utf-8")
