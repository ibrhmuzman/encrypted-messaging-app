from PIL import Image
import io

def stegano_embed(image_bytes: bytes, password: str) -> bytes:
    """
    Kullanıcı parolasını görüntünün piksellerinin LSB bitlerine gömer.
    DES anahtarından bağımsızdır.
    """

    # 1) byte -> Image aç
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert("RGB")

    # 2) Parolayı bit dizisine çevir
    binary_password = ''.join(format(ord(c), '08b') for c in password)
    password_length = len(binary_password)

    pixels = list(img.getdata())
    new_pixels = []

    bit_index = 0

    # 3) Her pikselin kırmızı kanalının LSB'sine sırayla yaz
    for (r, g, b) in pixels:
        if bit_index < password_length:
            # r'nin son bitini password bit'i ile değiştir
            new_r = (r & ~1) | int(binary_password[bit_index])
            bit_index += 1
        else:
            new_r = r  # yazacak bit kalmadıysa aynen koplaya

        new_pixels.append((new_r, g, b))

    img.putdata(new_pixels)

    # 4) Çıktıyı tekrar bytes olarak döndür
    output = io.BytesIO()
    img.save(output, format="PNG")  # PNG = lossless, bozulma olmaz
    return output.getvalue()


def stegano_extract(image_bytes: bytes) -> str:
    """
    Görüntünün LSB bitlerinden gömülü kullanıcı parolasını çıkarır.
    DES anahtarıyla bağlantısı yoktur.
    """

    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert("RGB")

    pixels = list(img.getdata())

    bits = ""

    # Kullanıcı parolasının uzunluğunu bilmiyoruz → sentinel karakteri gerekir
    # Parola bitlerinin sonunda özel bir bit dizisi ekleyeceğiz: "END"
    # END = üç karakter: E (69), N (78), D (68)
    # "E" = 01000101, "N" = 01001110, "D" = 01000100

    END_MARKER = "END"
    END_BITS = ''.join(format(ord(c), '08b') for c in END_MARKER)

    for (r, g, b) in pixels:
        bits += str(r & 1)

        # Eğer bits içinde END marker'ın binary karşılığı geçtiyse → dur
        if END_BITS in bits:
            break

    # Şimdi bitleri 8-bitlik parçalara ayır
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        char = chr(int(byte, 2))
        
        # END marker'a geldiysek parola biter
        if ''.join(chars[-2:] + [char]) == END_MARKER:
            chars = chars[:-2]  # END'e ait karakterleri sil
            break

        chars.append(char)

    return ''.join(chars)
