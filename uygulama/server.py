from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import base64
import time

from security.stegano import stegano_extract
from security.des import encrypt_des, decrypt_des


app = FastAPI()

# ============================================================
# VERİ YAPILARI
# ============================================================

users = {}  
"""
users = {
    "c1": {
        "key": "...",              # stegano’dan çıkarılan DES anahtarı
        "online": False,           # login/heartbeat ile güncellenir
        "last_heartbeat": 0        # en son ne zaman heartbeat geldi
    }
}
"""

inbox = {}
"""
inbox = {
    "c2": [
        {"from": "c1", "cipher": "...base64..."},
        {"from": "c3", "cipher": "...base64..."}
    ]
}
"""


# ============================================================
# BASE64 -> BYTES YARDIMCI FONKSİYONU
# ============================================================

def decode_base64_to_bytes(b64_string):
    return base64.b64decode(b64_string)


# ============================================================
# 1) REGISTER ENDPOINT
# ============================================================

@app.post("/register")
async def register_user(username: str = Form(...), image_base64: str = Form(...)):
    try:
        # Base64 görüntü decode edilir
        image_bytes = decode_base64_to_bytes(image_base64)

        # Security ekibinin yazacağı stegano extraction çağrılır
        extracted_key = stegano_extract(image_bytes)

        # Kullanıcı kaydedilir
        users[username] = {
            "key": extracted_key,
            "online": False,
            "last_heartbeat": 0
        }

        # Mesaj kutusu oluşturulur
        inbox[username] = []

        return JSONResponse({"status": "ok", "message": "User registered"})

    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)})



# ============================================================
# 2) LOGIN ENDPOINT
# ============================================================

@app.post("/login")
async def login(username: str = Form(...)):
    if username not in users:
        return JSONResponse({"status": "error", "message": "User not registered"})

    # Kullanıcı online oldu
    users[username]["online"] = True
    users[username]["last_heartbeat"] = time.time()

    return JSONResponse({"status": "ok", "message": "Login successful"})


# ============================================================
# 3) HEARTBEAT ENDPOINT
# ============================================================

HEARTBEAT_TIMEOUT = 10    # saniye – kullanıcı bu süre boyunca heartbeat göndermezse offline sayılır

@app.post("/heartbeat")
async def heartbeat(username: str = Form(...)):
    if username not in users:
        return JSONResponse({"status": "error", "message": "User not registered"})

    # Kullanıcıyı online işaretle ve zaman güncelle
    users[username]["online"] = True
    users[username]["last_heartbeat"] = time.time()

    # Offline mesajları teslim et
    pending_messages = inbox[username]
    inbox[username] = []  # kutuyu boşalt

    return {
        "status": "ok",
        "messages": pending_messages
    }


# ============================================================
# BACKGROUND LOGIC: Heartbeat timeout kontrolü
# ============================================================

def update_online_status():
    """
    Bu fonksiyon her endpoint çağrısında tetiklenebilir.
    Her kullanıcı için last_heartbeat kontrol edilir.
    Eğer çok uzun süre heartbeat yoksa kullanıcı offline yapılır.
    """
    now = time.time()
    for username, data in users.items():
        if data["online"]:
            # kullanıcının online kalması için son heartbeat zamanına bakıyoruz
            if now - data["last_heartbeat"] > HEARTBEAT_TIMEOUT:
                data["online"] = False



# ============================================================
# 4) USERS ENDPOINT (online/offline gösterir)
# ============================================================

@app.get("/users")
async def list_users():
    # Her çağrıda timeout kontrolü yapıyoruz
    update_online_status()

    # Liste döndürülür
    response_list = [
        {"username": u, "online": users[u]["online"]}
        for u in users
    ]

    return {"users": response_list}



# ============================================================
# 5) SEND MESSAGE ENDPOINT
# ============================================================

@app.post("/send")
async def send_message(
    sender: str = Form(...),
    receiver: str = Form(...),
    cipher_base64: str = Form(...)
):
    # Geçerlilik kontrolleri
    if sender not in users:
        return JSONResponse({"error": "Sender not registered"})
    if receiver not in users:
        return JSONResponse({"error": "Receiver not registered"})

    try:
        # 1) Base64 çöz
        cipher_bytes = base64.b64decode(cipher_base64)

        # 2) Gönderen anahtarı ile decrypt
        sender_key = users[sender]["key"]
        plain_message = decrypt_des(cipher_bytes, sender_key)

        # 3) Alıcı anahtarı ile yeniden encrypt
        receiver_key = users[receiver]["key"]
        new_cipher = encrypt_des(plain_message, receiver_key)

        # Base64 formatına çevir
        new_cipher_b64 = base64.b64encode(new_cipher).decode()

        # 4) Alıcının inbox'ına ekle
        inbox[receiver].append({
            "from": sender,
            "cipher": new_cipher_b64
        })

        return JSONResponse({"status": "ok", "message": "Message stored"})

    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)})



# ============================================================
# 6) MESSAGES ENDPOINT (manuel offline mesaj çekme)
# ============================================================

# @app.get("/messages")
# async def get_messages(username: str):
#     if username not in inbox:
#         return JSONResponse({"error": "User not registered"})

#     # Mesajları al
#     messages = inbox[username]

#     # Kutuyu temizle
#     inbox[username] = []

#     return {"messages": messages}
