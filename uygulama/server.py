from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import json
import time
import os

app = FastAPI()

DATA_FILE = "data.json"
HEARTBEAT_TIMEOUT = 15  # saniye


# ============================================================
# DATA.JSON YARDIMCILARI
# ============================================================

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "inbox": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def update_online_status(data):
    now = time.time()
    for user, info in data["users"].items():
        if info["online"] and now - info["last_heartbeat"] > HEARTBEAT_TIMEOUT:
            info["online"] = False


# ============================================================
# REGISTER
# ============================================================

@app.post("/register")
async def register(username: str = Form(...), image_base64: str = Form(...)):
    data = load_data()

    if username in data["users"]:
        return JSONResponse({"status": "error", "message": "User already exists"})

    # Key üretimi client tarafına bırakıldı (şimdilik placeholder)
    data["users"][username] = {
        "key": "CLIENT_SIDE_KEY",
        "online": False,
        "last_heartbeat": 0
    }
    data["inbox"][username] = []

    save_data(data)
    return JSONResponse({"status": "ok", "message": "Registered"})


# ============================================================
# LOGIN
# ============================================================

@app.post("/login")
async def login(username: str = Form(...)):
    data = load_data()

    if username not in data["users"]:
        return JSONResponse({"status": "error", "message": "User not registered"})

    data["users"][username]["online"] = True
    data["users"][username]["last_heartbeat"] = time.time()

    save_data(data)
    return JSONResponse({"status": "ok", "message": "Login successful"})


# ============================================================
# HEARTBEAT
# ============================================================

@app.post("/heartbeat")
async def heartbeat(username: str = Form(...)):
    data = load_data()

    if username not in data["users"]:
        return JSONResponse({"status": "error", "message": "User not registered"})

    data["users"][username]["online"] = True
    data["users"][username]["last_heartbeat"] = time.time()

    messages = data["inbox"][username]
    data["inbox"][username] = []

    save_data(data)
    return {"status": "ok", "messages": messages}


# ============================================================
# USERS
# ============================================================

@app.get("/users")
async def users():
    data = load_data()
    update_online_status(data)
    save_data(data)

    return {
        "users": [
            {"username": u, "online": info["online"]}
            for u, info in data["users"].items()
        ]
    }


# ============================================================
# SEND MESSAGE
# ============================================================

@app.post("/send")
async def send(
    sender: str = Form(...),
    receiver: str = Form(...),
    cipher_base64: str = Form(...)
):
    data = load_data()

    if sender not in data["users"] or receiver not in data["users"]:
        return JSONResponse({"status": "error", "message": "Invalid user"})

    data["inbox"][receiver].append({
        "from": sender,
        "cipher": cipher_base64
    })

    save_data(data)
    return JSONResponse({"status": "ok"})
