import hashlib

def hash_password(password: str) -> str:
    """
    Parolayı SHA-256 algoritması ile hashler.
    Hash sonucunu hex string olarak döndürür.
    
    Bu hash veritabanında saklanabilir.
    """
    hashed = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hashed


def verify_password(password: str, hashed: str) -> bool:
    """
    Kullanıcının login sırasında girdiği parolayı tekrar hashler
    ve veritabanındaki hash ile karşılaştırır.
    
    True → parola doğru
    False → parola yanlış
    """
    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return password_hash == hashed
