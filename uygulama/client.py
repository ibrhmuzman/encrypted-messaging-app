# api_client.py

import base64
import requests


class ApiClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.current_user = None

    # --------------------------------------------------------
    # 1) REGISTER
    # --------------------------------------------------------
    def register(self, username, password, image_path):
        """
        password şimdilik backend’de kullanılmıyor,
        ileride stegano + DES tarafı için işinize yarayacak.
        Burada sadece image'ı base64'e çevirip gönderiyoruz.
        """
        # resmi oku ve base64'e çevir
        with open(image_path, "rb") as f:
            img_bytes = f.read()
        img_b64 = base64.b64encode(img_bytes).decode()

        url = f"{self.base_url}/register"
        data = {
            "username": username,
            "image_base64": img_b64
        }

        resp = requests.post(url, data=data)
        j = resp.json()

        if j.get("status") == "ok":
            self.current_user = username
            return True, j.get("message", "Registered")
        else:
            return False, j.get("detail") or j.get("message", "Error")

    # --------------------------------------------------------
    # 2) LOGIN
    # --------------------------------------------------------
    def login(self, username):
        url = f"{self.base_url}/login"
        data = {"username": username}
        resp = requests.post(url, data=data)
        j = resp.json()
        if j.get("status") == "ok":
            self.current_user = username
            return True, j.get("message", "Login successful")
        else:
            return False, j.get("message", "Login error")

    # --------------------------------------------------------
    # 3) HEARTBEAT
    # --------------------------------------------------------
    def heartbeat(self):
        """
        Backend /heartbeat username alıp:
        - kullanıcıyı online sayıyor
        - pending mesajları döndürüyor
        """
        if not self.current_user:
            return False, []

        url = f"{self.base_url}/heartbeat"
        data = {"username": self.current_user}
        resp = requests.post(url, data=data)
        j = resp.json()

        if j.get("status") == "ok":
            # messages: [{ "from": "...", "cipher": "...." }, ...]
            return True, j.get("messages", [])
        else:
            return False, []

    # --------------------------------------------------------
    # 4) USERS
    # --------------------------------------------------------
    def get_users(self):
        url = f"{self.base_url}/users"
        resp = requests.get(url)
        j = resp.json()

        # j: { "users": [ {"username": "...", "online": bool}, ...] }
        users = j.get("users", [])
        # sadece kullanıcı adlarını döndürelim (istersen online bilgisini de kullanabilirsin)
        names = [u["username"] for u in users if u["username"] != self.current_user]
        return names, users  # (sadece isim listesi, ve full liste)

    # --------------------------------------------------------
    # 5) SEND MESSAGE
    # --------------------------------------------------------
    def send_message(self, to_user, plain_message):
        """
        Normalde burada:
        - plain_message'i DES ile şifreleyip
        - cipher'ı base64'e çevirip
        - /send'e yollayacağız.

        Şimdilik, DES kısmı hazır değilse basitçe
        plain text'i utf-8 byte -> base64 yapıp gönderiyoruz.
        Güvenlikçi arkadaş DES'i bitirdiğinde
        burayı güncelleyeceksiniz.
        """
        if not self.current_user:
            return False

        # GEÇİCİ: plain text'i direkt base64 yap
        msg_bytes = plain_message.encode("utf-8")
        cipher_b64 = base64.b64encode(msg_bytes).decode()

        url = f"{self.base_url}/send"
        data = {
            "sender": self.current_user,
            "receiver": to_user,
            "cipher_base64": cipher_b64
        }

        resp = requests.post(url, data=data)
        j = resp.json()

        return j.get("status") == "ok"
