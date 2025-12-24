from des_utils import generate_random_key

def main():
    print("=== RANDOM KEY TEST ===")

    k1 = generate_random_key()
    k2 = generate_random_key()
    k3 = generate_random_key()

    print("Key1:", k1)
    print("Key2:", k2)
    print("Key3:", k3)

    all_unique = (k1 != k2) and (k2 != k3) and (k1 != k3)
    print("Anahtarlar benzersiz mi →", all_unique)


if __name__ == "__main__":
    main()
