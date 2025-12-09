# security.py

def stegano_extract(image_bytes: bytes) -> str:
    # Şimdilik deneme için sabit bir key döndürelim
    return "TEST_KEY_12345678"  # DES için 8 karakterlik bir key gibi

def encrypt_des(plain_text: str, key: str) -> bytes:
    # Şimdilik gerçek DES yok, direkt utf-8 encode
    return plain_text.encode("utf-8")

def decrypt_des(cipher_bytes: bytes, key: str) -> str:
    # Şimdilik direkt decode
    return cipher_bytes.decode("utf-8")
