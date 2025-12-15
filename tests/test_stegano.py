from stegano_utils import stegano_embed, stegano_extract
from PIL import Image
import io

def main():
    print("=== STEGANO TEST ===")

    password = "sena8877"

    # Test için sade beyaz bir resim oluştur
    img = Image.new("RGB", (200, 200), (255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    image_bytes = buf.getvalue()

    # Parola göm
    embedded = stegano_embed(image_bytes, password)

    # Çıkar
    extracted = stegano_extract(embedded)

    print("Orijinal:", password)
    print("Çıkarılan:", extracted)
    print("Başarılı mı →", extracted == password)


if __name__ == "__main__":
    main()
