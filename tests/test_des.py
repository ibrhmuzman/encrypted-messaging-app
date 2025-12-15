from des_utils import encrypt_des, decrypt_des

def main():
    print("=== DES TEST ===")

    key = "A1B2C3D4"
    msg = "Hello Dünya"

    cipher = encrypt_des(msg, key)
    print("Şifreli:", cipher)

    plain = decrypt_des(cipher, key)
    print("Çözülmüş:", plain)

    print("Başarılı mı →", plain == msg)


if __name__ == "__main__":
    main()
