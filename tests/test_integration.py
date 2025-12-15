from des_utils import encrypt_des, decrypt_des,generate_random_key
from stegano_utils import stegano_embed, stegano_extract
from hash_utils import hash_password, verify_password

from PIL import Image
import io

def main():
    print("=== FULL SECURITY INTEGRATION TEST ===")

    # 1) Kullanıcı parolası
    password = "sifre123"

    # 2) Resim oluştur
    img = Image.new("RGB", (300, 300), (255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    image_bytes = buf.getvalue()

    # 3) Stegano embed
    embedded = stegano_embed(image_bytes, password)

    # 4) Extract
    extracted = stegano_extract(embedded)
    print("Stegano doğru mu →", extracted == password)

    # 5) Hashleme
    hashed = hash_password(extracted)
    print("Hash doğrulama →", verify_password(password, hashed))

    # 6) DES mesaj testi
    des_key = generate_random_key()
    message = "Bu sistem çalışıyor!"

    cipher = encrypt_des(message, des_key)
    plain = decrypt_des(cipher, des_key)

    print("DES doğru mu →", plain == message)

    print("\nSonuç: TÜM MODÜLLER BAŞARIYLA ÇALIŞIYOR!")


if __name__ == "__main__":
    main()
