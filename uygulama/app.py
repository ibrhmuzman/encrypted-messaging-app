import sys
import os
import json
import base64

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QTextEdit,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt

from client import ApiClient
from stegano_utils import stegano_embed


# ======================================================
# CHAT WINDOW
# ======================================================
class ChatWindow(QWidget):
    def __init__(self, api: ApiClient):
        super().__init__()
        self.api = api

        self.current_chat_user = None
        self.unread = {}

        self.chat_file = f"chat_{self.api.current_user}.json"
        self.conversations = self.load_chats()

        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.poll_messages)
        self.timer.start(2000)

    # ---------------- LOAD / SAVE ----------------
    def load_chats(self):
        if os.path.exists(self.chat_file):
            with open(self.chat_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_chats(self):
        with open(self.chat_file, "w", encoding="utf-8") as f:
            json.dump(self.conversations, f, ensure_ascii=False, indent=2)

    # ---------------- UI ----------------
    def init_ui(self):
        self.setWindowTitle(f"Chat - {self.api.current_user}")
        self.setGeometry(400, 200, 780, 480)

        main = QHBoxLayout(self)

        # ---- USERS
        self.user_list = QListWidget()
        self.user_list.setFixedWidth(190)
        self.user_list.itemClicked.connect(self.on_user_selected)
        main.addWidget(self.user_list)

        # ---- CHAT AREA
        right = QVBoxLayout()

        self.chat_title = QTextEdit()
        self.chat_title.setReadOnly(True)
        self.chat_title.setFixedHeight(45)
        self.chat_title.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_title.setHtml("<center><i>Select a user</i></center>")
        right.addWidget(self.chat_title)

        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
        right.addWidget(self.chat_box)

        bottom = QHBoxLayout()

        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("Type a message...")
        bottom.addWidget(self.msg_input)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)
        bottom.addWidget(send_btn)

        active_btn = QPushButton("Active Users")
        active_btn.clicked.connect(self.show_active_users)
        bottom.addWidget(active_btn)

        right.addLayout(bottom)
        main.addLayout(right)

        self.load_users()

    # ---------------- USERS ----------------
    def load_users(self):
        names, users = self.api.get_users()
        self.user_list.clear()

        for u in users:
            name = u["username"]
            if name == self.api.current_user:
                continue

            if name in self.unread:
                self.user_list.addItem(f"● {name}")
            else:
                self.user_list.addItem(name)

    def on_user_selected(self, item):
        user = item.text().replace("● ", "")
        self.current_chat_user = user
        self.unread.pop(user, None)
        self.load_users()

        # SADECE BURADA kim kiminle konuşuyor yazıyor
        self.chat_title.setHtml(
            f"<center><b>You</b> ↔ <b>{user}</b></center>"
        )

        self.chat_box.clear()

        for msg in self.conversations.get(user, []):
            if msg["from"] == "me":
                self.chat_box.insertHtml(
                    self.my_bubble(msg["text"]) + "<br>"
                )
            else:
                self.chat_box.insertHtml(
                    self.other_bubble(msg["from"], msg["text"]) + "<br>"
                )


    # ---------------- SEND ----------------
    def send_message(self):
        if not self.current_chat_user:
            QMessageBox.warning(self, "Error", "Select a user")
            return

        text = self.msg_input.text().strip()
        if not text:
            return

        to_user = self.current_chat_user

        self.conversations.setdefault(to_user, []).append({
            "from": "me",
            "text": text
        })

        self.chat_box.insertHtml(self.my_bubble(text) + "<br>")
        self.api.send_message(to_user, text)
        self.msg_input.clear()
        self.save_chats()

    # ---------------- RECEIVE ----------------
    def poll_messages(self):
        try:
            messages = self.api.receive_messages()
        except:
            return

        for msg in messages:
            sender = msg["from"]
            text = msg["text"]

            self.conversations.setdefault(sender, []).append({
                "from": sender,
                "text": text
            })

            if self.current_chat_user == sender:
                self.chat_box.insertHtml(
                    self.other_bubble(sender, text) + "<br>"
                )
            else:
                self.unread[sender] = True
                self.load_users()

        self.save_chats()

    # ---------------- BUBBLES ----------------
    def my_bubble(self, text):
        return f"""
        <div style="
            background:#8e6ec8;
            color:white;
            padding:10px 14px;
            border-radius:18px 18px 4px 18px;
            max-width:65%;
            margin-left:auto;
            margin-top:6px;
        ">{text}</div>
        """

    def other_bubble(self, sender, text):
        return f"""
        <div style="
            background:#f1ecf9;
            color:#3d2c4f;
            padding:10px 14px;
            border-radius:18px 18px 18px 4px;
            max-width:65%;
            margin-top:6px;
        ">
        <b>{sender}</b><br>{text}</div>
        """

    # ---------------- ACTIVE USERS ----------------
    def show_active_users(self):
        _, users = self.api.get_users()
        active = [u["username"] for u in users if u["online"]]

        if not active:
            QMessageBox.information(self, "Active Users", "No active users")
        else:
            QMessageBox.information(self, "Active Users", "\n".join(active))


# ======================================================
# LOGIN / REGISTER
# ======================================================
class RegisterLoginApp(QWidget):
    def __init__(self):
        super().__init__()
        self.api = ApiClient()
        self.image_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Secure Chat")
        self.setGeometry(300, 300, 350, 260)

        layout = QVBoxLayout(self)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        img_btn = QPushButton("Select Image")
        img_btn.clicked.connect(self.select_image)
        layout.addWidget(img_btn)

        reg_btn = QPushButton("Register")
        reg_btn.clicked.connect(self.register)
        layout.addWidget(reg_btn)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)

    def select_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image")
        if path:
            self.image_path = path

    def register(self):
        if not self.image_path:
            QMessageBox.warning(self, "Error", "Image required")
            return

        with open(self.image_path, "rb") as f:
            img = f.read()

        embedded = stegano_embed(img, self.password.text())
        img_b64 = base64.b64encode(embedded).decode()

        ok, msg = self.api.register(self.username.text(), img_b64)
        QMessageBox.information(self, "Info", msg)

    def login(self):
        ok, msg = self.api.login(self.username.text(), self.password.text())
        if not ok:
            QMessageBox.warning(self, "Error", msg)
            return

        self.chat = ChatWindow(self.api)
        self.chat.show()
        self.close()


# ======================================================
# MAIN
# ======================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QWidget { background:#f6f1fb; color:#3d2c4f; }
        QLineEdit { background:white; border:1px solid #c9b6e4; border-radius:8px; padding:6px; }
        QTextEdit { background:white; border:1px solid #c9b6e4; border-radius:10px; }
        QListWidget { background:white; border:1px solid #c9b6e4; border-radius:10px; }
        QPushButton { background:#8e6ec8; color:white; border-radius:8px; padding:6px 12px; }
        QPushButton:hover { background:#7a5bb3; }
    """)

    w = RegisterLoginApp()
    w.show()
    sys.exit(app.exec_())
