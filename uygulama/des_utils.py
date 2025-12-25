from Crypto.Cipher import DES
import base64
from secrets import token_bytes

# ---------------------------------------------------
# KEY GENERATION
# ---------------------------------------------------
def generate_random_key() -> bytes:
    """
    DES için kriptografik olarak güvenli 8 byte'lık (64-bit) key üretir.
    Key bytes olarak döndürülür.
    """
    return token_bytes(8)   # ✅ bytes


# ---------------------------------------------------
# PADDING
# ---------------------------------------------------
def pad_text(text: str) -> bytes:
    data = text.encode("utf-8")
    padding_len = 8 - (len(data) % 8)
    data += bytes([padding_len]) * padding_len
    return data


def unpad_text(data: bytes) -> str:
    padding_len = data[-1]
    return data[:-padding_len].decode("utf-8")


# ---------------------------------------------------
# ENCRYPT / DECRYPT
# ---------------------------------------------------
def encrypt_des(plain_text: str, key: bytes) -> bytes:
    """
    Mesajı DES ECB modunda şifreler.
    ÇIKTI: base64 encoded bytes
    """
    des = DES.new(key, DES.MODE_ECB)

    padded = pad_text(plain_text)
    cipher_bytes = des.encrypt(padded)

    return base64.b64encode(cipher_bytes)


def decrypt_des(cipher_bytes: bytes, key: bytes) -> str:
    """
    Base64 decode → DES decrypt → unpad
    """
    des = DES.new(key, DES.MODE_ECB)

    cipher_raw = base64.b64decode(cipher_bytes)
    decrypted_padded = des.decrypt(cipher_raw)

    return unpad_text(decrypted_padded)
