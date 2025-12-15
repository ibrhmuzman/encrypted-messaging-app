import requests
import base64
import time

BASE_URL = "http://127.0.0.1:8000"

def print_step(title):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)

# --------------------------------------------------
# 1) REGISTER
# --------------------------------------------------
print_step("1) REGISTER TEST")

dummy_image_bytes = b"FAKE_IMAGE_DATA"
dummy_image_b64 = base64.b64encode(dummy_image_bytes).decode()

r = requests.post(
    f"{BASE_URL}/register",
    data={
        "username": "test_user",
        "image_base64": dummy_image_b64
    }
)
print("Register response:", r.json())

# --------------------------------------------------
# 2) LOGIN
# --------------------------------------------------
print_step("2) LOGIN TEST")

r = requests.post(
    f"{BASE_URL}/login",
    data={"username": "test_user"}
)
print("Login response:", r.json())

# --------------------------------------------------
# 3) USERS (online durumu)
# --------------------------------------------------
print_step("3) USERS LIST")

r = requests.get(f"{BASE_URL}/users")
print("Users response:", r.json())

# --------------------------------------------------
# 4) SEND MESSAGE
# --------------------------------------------------
print_step("4) SEND MESSAGE")

# önce ikinci kullanıcıyı register edelim
requests.post(
    f"{BASE_URL}/register",
    data={
        "username": "receiver_user",
        "image_base64": dummy_image_b64
    }
)

cipher = base64.b64encode(b"hello world").decode()

r = requests.post(
    f"{BASE_URL}/send",
    data={
        "sender": "test_user",
        "receiver": "receiver_user",
        "cipher_base64": cipher
    }
)
print("Send response:", r.json())

# --------------------------------------------------
# 5) HEARTBEAT (offline mesaj alma)
# --------------------------------------------------
print_step("5) HEARTBEAT (receiver_user)")

r = requests.post(
    f"{BASE_URL}/heartbeat",
    data={"username": "receiver_user"}
)
print("Heartbeat response:", r.json())

# --------------------------------------------------
# 6) HEARTBEAT tekrar (inbox boş mu?)
# --------------------------------------------------
print_step("6) HEARTBEAT AGAIN (should be empty)")

r = requests.post(
    f"{BASE_URL}/heartbeat",
    data={"username": "receiver_user"}
)
print("Heartbeat response:", r.json())
