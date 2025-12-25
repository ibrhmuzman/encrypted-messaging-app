import base64
import requests

from des_utils import encrypt_des, decrypt_des


class ApiClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.current_user = None
        self.session_key = None

    # ---------------------------------------------------
    # REGISTER
    # ---------------------------------------------------
    def register(self, username, image_base64):
        resp = requests.post(
            f"{self.base_url}/register",
            data={
                "username": username,
                "image_base64": image_base64
            },
            timeout=10
        )

        try:
            j = resp.json()
        except Exception:
            return False, "Server error"

        if j.get("status") == "ok":
            return True, "Registered"

        return False, j.get("message", "Register failed")

    # ---------------------------------------------------
    # LOGIN
    # ---------------------------------------------------
    def login(self, username, password):
        resp = requests.post(
            f"{self.base_url}/login",
            data={
                "username": username,
                "password": password
            },
            timeout=10
        )

        try:
            j = resp.json()
        except Exception:
            return False, "Server error"

        if j.get("status") == "ok":
            self.current_user = username

            # 🔑 SERVER'DAN GELEN DES KEY
            key_b64 = j.get("des_key")
            self.session_key = base64.b64decode(key_b64)

            return True, "Login successful"

        return False, "Login failed"

    # ---------------------------------------------------
    # SEND MESSAGE
    # (Client tarafında plaintext → encrypt → server)
    # ---------------------------------------------------
    def send_message(self, to_user, plain_text):
        if not self.current_user or not self.session_key:
            return False

        # 🔐 CLIENT TARAFINDA ŞİFRELE
        cipher_bytes = encrypt_des(plain_text, self.session_key)
        cipher_b64 = cipher_bytes.decode()

        resp = requests.post(
            f"{self.base_url}/send",
            data={
                "sender": self.current_user,
                "receiver": to_user,
                "cipher_base64": cipher_b64
            },
            timeout=10
        )

        try:
            j = resp.json()
        except Exception:
            return False

        return j.get("status") == "ok"

    # ---------------------------------------------------
    # RECEIVE MESSAGES
    # (Server → receiver key ile şifreli gönderir)
    # ---------------------------------------------------
    def receive_messages(self):
        if not self.current_user or not self.session_key:
            return []

        resp = requests.post(
            f"{self.base_url}/heartbeat",
            data={"username": self.current_user},
            timeout=10
        )

        try:
            j = resp.json()
        except Exception:
            return []

        if j.get("status") != "ok":
            return []

        result = []
        for msg in j.get("messages", []):
            cipher_bytes = msg["cipher"].encode()
            plaintext = decrypt_des(cipher_bytes, self.session_key)

            result.append({
                "from": msg["from"],
                "text": plaintext
            })

        return result

    # ---------------------------------------------------
    # GET USERS
    # ---------------------------------------------------
    def get_users(self):
        resp = requests.get(f"{self.base_url}/users", timeout=10)

        try:
            j = resp.json()
        except Exception:
            return [], []

        users = j.get("users", [])
        names = [u["username"] for u in users if u["username"] != self.current_user]

        return names, users
