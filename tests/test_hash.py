from hash_utils import hash_password, verify_password

def main():
    print("=== HASH TEST ===")

    password = "merve1234"
    hashed = hash_password(password)

    print("Hash:", hashed)
    print("Doğru mu →", verify_password("merve1234", hashed))
    print("Yanlış mı →", verify_password("yanlis", hashed))


if __name__ == "__main__":
    main()
