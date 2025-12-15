from Crypto.Cipher import DES
import base64
from secrets import token_bytes

def generate_random_key() -> str:
    """
    DES için kriptografik olarak güvenli 8 byte'lık (64-bit) key üretir.
    Key, string formatında döndürülür (stegano içine gömülebilsin diye).
    """
    key_bytes = token_bytes(8)  # 8 byte = 64 bit DES anahtarı
    return key_bytes.hex()      # Hex string (16 karakter)


def normalize_key(key: str) -> bytes:
    """
    DES için anahtar mutlaka 8 byte olmalıdır.
    Kısa ise '_' ile tamamlanır, uzun ise kesilir.
    """
    key = key.encode("utf-8")
    if len(key) < 8:
        key = key.ljust(8, b'_')
    elif len(key) > 8:
        key = key[:8]
    return key


def pad_text(text: str) -> bytes:
    """
    DES 8 byte bloklarda çalışır. Mesajı pad ile tamamlar.
    """
    data = text.encode("utf-8")
    padding_len = 8 - (len(data) % 8)
    data += bytes([padding_len]) * padding_len
    return data


def unpad_text(data: bytes) -> str:
    """
    Padding'i kaldırır ve temiz metni döndürür.
    """
    padding_len = data[-1]
    return data[:-padding_len].decode("utf-8")


def encrypt_des(plain_text: str, key: str) -> bytes:
    """
    Mesajı DES ECB modunda şifreler.
    Base64 ile encode edilerek taşınmaya uygun hale getirilir.
    """
    key_bytes = normalize_key(key)
    des = DES.new(key_bytes, DES.MODE_ECB)

    padded = pad_text(plain_text)
    cipher_bytes = des.encrypt(padded)

    return base64.b64encode(cipher_bytes)   # bytes döner


def decrypt_des(cipher_bytes: bytes, key: str) -> str:
    """
    DES şifreli mesajı çözer.
    Base64 decode → DES decrypt → unpad.
    """
    key_bytes = normalize_key(key)
    des = DES.new(key_bytes, DES.MODE_ECB)

    cipher_raw = base64.b64decode(cipher_bytes)
    decrypted_padded = des.decrypt(cipher_raw)

    return unpad_text(decrypted_padded)
