import base64
import requests
from des_utils import encrypt_des

class ApiClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.current_user = None
        self.session_key = None

    # ---------------------------
    # REGISTER (embedded image base64 gönderilir)
    # ---------------------------
    def register(self, username, image_base64):
        resp = requests.post(
            f"{self.base_url}/register",
            data={"username": username, "image_base64": image_base64},
            timeout=10
        )
        # server hata verirse json olmayabilir -> güvenli parse
        try:
            j = resp.json()
        except Exception:
            return False, f"Server error: {resp.status_code}"

        if j.get("status") == "ok":
            self.current_user = username
            return True, j.get("message", "Registered")
        return False, j.get("message", "Error")

    # ---------------------------
    # LOGIN
    # ---------------------------
    def login(self, username):
        resp = requests.post(
            f"{self.base_url}/login",
            data={"username": username},
            timeout=10
        )
        try:
            j = resp.json()
        except Exception:
            return False, f"Server error: {resp.status_code}"

        if j.get("status") == "ok":
            self.current_user = username
            return True, j.get("message", "Login ok")
        return False, j.get("message", "Login error")

    # ---------------------------
    # FETCH PROFILE IMAGE
    # ---------------------------
    def fetch_profile_image(self, username):
        resp = requests.get(f"{self.base_url}/profile-image/{username}", timeout=10)
        try:
            j = resp.json()
        except Exception:
            raise Exception(f"Server error: {resp.status_code}")

        if j.get("status") != "ok":
            raise Exception(j.get("message", "Failed to fetch profile image"))

        return base64.b64decode(j["image_base64"])

    # ---------------------------
    # HEARTBEAT
    # ---------------------------
    def heartbeat(self):
        if not self.current_user:
            return False, []

        resp = requests.post(
            f"{self.base_url}/heartbeat",
            data={"username": self.current_user},
            timeout=10
        )
        try:
            j = resp.json()
        except Exception:
            return False, []

        if j.get("status") == "ok":
            return True, j.get("messages", [])
        return False, []

    # ---------------------------
    # USERS
    # ---------------------------
    def get_users(self):
        resp = requests.get(f"{self.base_url}/users", timeout=10)
        j = resp.json()
        users = j.get("users", [])
        names = [u["username"] for u in users if u["username"] != self.current_user]
        return names, users

    # ---------------------------
    # SEND MESSAGE (client encrypt eder, server relay)
    # ---------------------------
    def send_message(self, to_user, plain_text):
        if not self.current_user:
            raise Exception("Not logged in")
        if not self.session_key:
            raise Exception("Session key not set")

        cipher_bytes = encrypt_des(plain_text, self.session_key)

        # encrypt_des zaten base64 döndürüyor olabilir; biz str göndereceğiz:
        if isinstance(cipher_bytes, (bytes, bytearray)):
            cipher_b64 = base64.b64encode(cipher_bytes).decode()
        else:
            cipher_b64 = str(cipher_bytes)

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
