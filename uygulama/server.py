from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import time
import json
import base64
from pathlib import Path

from des_utils import generate_random_key, decrypt_des, encrypt_des
from hash_utils import hash_password
from stegano_utils import stegano_extract


# ------------------------------------------------------------
# PATHS  ✅ ÖNCE
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.json"
PROFILE_DIR = BASE_DIR / "profiles"
PROFILE_DIR.mkdir(exist_ok=True)

HEARTBEAT_TIMEOUT = 10


# ------------------------------------------------------------
# LOG SYSTEM  ✅ BASE_DIR'DAN SONRA
# ------------------------------------------------------------
LOG_FILE = BASE_DIR / "crypto_log.txt"

def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


# ------------------------------------------------------------
# FASTAPI APP  ✅ EN SON
# ------------------------------------------------------------
app = FastAPI()

# ------------------------------------------------------------
# STORAGE
# ------------------------------------------------------------
def load_data():
    if not DATA_FILE.exists():
        return {"users": {}, "inbox": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ------------------------------------------------------------
# REGISTER
# ------------------------------------------------------------
@app.post("/register")
async def register(username: str = Form(...), image_base64: str = Form(...)):
    data = load_data()

    if username in data["users"]:
        return JSONResponse({"status": "error", "message": "User exists"}, 400)

    # stegano -> password
    image_bytes = base64.b64decode(image_base64)
    password = stegano_extract(image_bytes)
    pw_hash = hash_password(password)

    # DES KEY REGISTER'DA ÜRETİLİR (KALICI)
    des_key = generate_random_key()
    des_key_b64 = base64.b64encode(des_key).decode()

    data["users"][username] = {
        "password_hash": pw_hash,
        "des_key": des_key_b64,
        "online": False,
        "last_heartbeat": 0
    }

    data["inbox"][username] = []

    (PROFILE_DIR / f"{username}.b64").write_text(image_base64)
    save_data(data)

    return {"status": "ok"}

# ------------------------------------------------------------
# LOGIN
# ------------------------------------------------------------
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    data = load_data()

    if username not in data["users"]:
        return JSONResponse({"status": "error"}, 404)

    if hash_password(password) != data["users"][username]["password_hash"]:
        return JSONResponse({"status": "error"}, 401)

    data["users"][username]["online"] = True
    data["users"][username]["last_heartbeat"] = time.time()

    save_data(data)

    return {
        "status": "ok",
        "des_key": data["users"][username]["des_key"]
    }

# ------------------------------------------------------------
# SEND MESSAGE
# ------------------------------------------------------------
@app.post("/send")
async def send(
    sender: str = Form(...),
    receiver: str = Form(...),
    cipher_base64: str = Form(...)
):
    data = load_data()

    if sender not in data["users"] or receiver not in data["users"]:
        return JSONResponse({"status": "error"}, 404)

    sender_key = base64.b64decode(data["users"][sender]["des_key"])
    # Gönderenin key'i ile çöz
    log("----- NEW MESSAGE -----")
    log(f"FROM CLIENT (encrypted): {cipher_base64}")

    plaintext = decrypt_des(cipher_base64.encode(), sender_key)
    
    receiver_online = data["users"][receiver]["online"]

    log(f"ROUTING: from={sender} to={receiver} online={receiver_online}")


    log(f"SERVER DECRYPTED (plaintext): {plaintext}")

    # SERVER PLAINTEXT SAKLAR
    data["inbox"][receiver].append({
        "from": sender,
        "message": plaintext
    })

    save_data(data)
    return {"status": "ok"}

# ------------------------------------------------------------
# HEARTBEAT / GET MESSAGES
# ------------------------------------------------------------
@app.post("/heartbeat")
async def heartbeat(username: str = Form(...)):
    data = load_data()

    if username not in data["users"]:
        return JSONResponse({"status": "error"}, 404)

    receiver_key = base64.b64decode(data["users"][username]["des_key"])

    messages = []
    for msg in data["inbox"][username]:
        cipher = encrypt_des(msg["message"], receiver_key)
        log(f"SERVER RE-ENCRYPTED FOR RECEIVER: {cipher.decode()}")
        messages.append({
            "from": msg["from"],
            "cipher": cipher.decode()
        })

    data["inbox"][username] = []
    data["users"][username]["last_heartbeat"] = time.time()
    save_data(data)

    return {"status": "ok", "messages": messages}

# ------------------------------------------------------------
# USERS
# ------------------------------------------------------------
@app.get("/users")
async def users():
    data = load_data()
    now = time.time()

    users = []
    for u, info in data["users"].items():
        online = info["online"]
        last = info["last_heartbeat"]

        if online and now - last > HEARTBEAT_TIMEOUT:
            online = False
            info["online"] = False

        users.append({
            "username": u,
            "online": online,
            "last_seen": last
        })

    save_data(data)
    return {"users": users}

