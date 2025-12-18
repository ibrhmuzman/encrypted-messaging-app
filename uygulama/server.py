from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import time
import json
import os
from pathlib import Path

app = FastAPI()

# ------------------------------------------------------------
# PATHS (KRİTİK: her şey server.py'nin bulunduğu klasöre göre)
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.json"
PROFILE_DIR = BASE_DIR / "profiles"
PROFILE_DIR.mkdir(exist_ok=True)

HEARTBEAT_TIMEOUT = 10  # seconds


# ------------------------------------------------------------
# STORAGE
# ------------------------------------------------------------
def load_data():
    if not DATA_FILE.exists():
        return {"users": {}, "inbox": {}}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "users" not in data:
                data["users"] = {}
            if "inbox" not in data:
                data["inbox"] = {}
            return data
    except (json.JSONDecodeError, OSError):
        return {"users": {}, "inbox": {}}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_online_status(data):
    now = time.time()
    for u, info in data["users"].items():
        if info.get("online"):
            if now - info.get("last_heartbeat", 0) > HEARTBEAT_TIMEOUT:
                info["online"] = False


# ------------------------------------------------------------
# 1) REGISTER  (server key bilmez, sadece profile image saklar)
# ------------------------------------------------------------
@app.post("/register")
async def register(username: str = Form(...), image_base64: str = Form(...)):
    data = load_data()

    if username in data["users"]:
        return JSONResponse({"status": "error", "message": "User exists"}, status_code=400)

    # user metadata
    data["users"][username] = {
        "online": False,
        "last_heartbeat": 0
    }
    data["inbox"][username] = []

    # profile image save
    img_path = PROFILE_DIR / f"{username}.b64"
    try:
        with open(img_path, "w", encoding="utf-8") as f:
            f.write(image_base64)
    except OSError as e:
        return JSONResponse({"status": "error", "message": f"Cannot save image: {e}"}, status_code=500)

    save_data(data)
    return JSONResponse({"status": "ok", "message": "Registered"})


# ------------------------------------------------------------
# 2) LOGIN
# ------------------------------------------------------------
@app.post("/login")
async def login(username: str = Form(...)):
    data = load_data()

    if username not in data["users"]:
        return JSONResponse({"status": "error", "message": "User not registered"}, status_code=404)

    data["users"][username]["online"] = True
    data["users"][username]["last_heartbeat"] = time.time()
    save_data(data)

    return JSONResponse({"status": "ok", "message": "Login successful"})


# ------------------------------------------------------------
# 3) PROFILE IMAGE (client login'de çeker)
# ------------------------------------------------------------
@app.get("/profile-image/{username}")
async def profile_image(username: str):
    img_path = PROFILE_DIR / f"{username}.b64"

    if not img_path.exists():
        return JSONResponse({"status": "error", "message": "Image not found"}, status_code=404)

    with open(img_path, "r", encoding="utf-8") as f:
        image_base64 = f.read()

    return {"status": "ok", "image_base64": image_base64}


# ------------------------------------------------------------
# 4) HEARTBEAT (offline messages)
# ------------------------------------------------------------
@app.post("/heartbeat")
async def heartbeat(username: str = Form(...)):
    data = load_data()

    if username not in data["users"]:
        return JSONResponse({"status": "error", "message": "User not registered"}, status_code=404)

    data["users"][username]["online"] = True
    data["users"][username]["last_heartbeat"] = time.time()

    pending = data["inbox"].get(username, [])
    data["inbox"][username] = []
    save_data(data)

    return {"status": "ok", "messages": pending}


# ------------------------------------------------------------
# 5) USERS
# ------------------------------------------------------------
@app.get("/users")
async def users():
    data = load_data()
    update_online_status(data)
    save_data(data)

    return {
        "users": [
            {"username": u, "online": data["users"][u].get("online", False)}
            for u in data["users"]
        ]
    }


# ------------------------------------------------------------
# 6) SEND (server decrypt etmez, sadece cipher'ı taşır)
# ------------------------------------------------------------
@app.post("/send")
async def send(sender: str = Form(...), receiver: str = Form(...), cipher_base64: str = Form(...)):
    data = load_data()

    if sender not in data["users"]:
        return JSONResponse({"status": "error", "message": "Sender not registered"}, status_code=404)
    if receiver not in data["users"]:
        return JSONResponse({"status": "error", "message": "Receiver not registered"}, status_code=404)

    data["inbox"].setdefault(receiver, [])
    data["inbox"][receiver].append({
        "from": sender,
        "cipher": cipher_base64
    })

    save_data(data)
    return JSONResponse({"status": "ok"})
