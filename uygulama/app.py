import sys
import base64

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox,
    QListWidget, QListWidgetItem, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor

from client import ApiClient


# =======================
# LOGIN SAYFASI
# =======================
class LoginPage(QWidget):
    def __init__(self, api_client, on_login_success, go_register, parent=None):
        super().__init__(parent)
        self.api = api_client
        self.on_login_success = on_login_success
        self.go_register = go_register
        self.init_ui()

    def init_ui(self):
        # Arka plan
        self.setStyleSheet("background-color: #f2f5f7;")

        outer = QVBoxLayout()

        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background: #ffffff;
                border-radius: 16px;
                padding: 25px;
                border: 1px solid #ddd;
            }
        """)
        form = QVBoxLayout(container)

        title = QLabel("Welcome Back")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 15px;")
        form.addWidget(title)

        subtitle = QLabel("Sign in to your secure chat account")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666666; margin-bottom: 10px;")
        form.addWidget(subtitle)

        # Username
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Username")
        self.username_edit.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        form.addWidget(self.username_edit)

        # Password (şimdilik backend tarafında kullanılmıyor ama tasarım için dursun)
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        form.addWidget(self.password_edit)

        # Login butonu
        btn_login = QPushButton("Login")
        btn_login.setStyleSheet("""
            QPushButton {
                background-color: #0078ff;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005fcc;
            }
        """)
        btn_login.clicked.connect(self.login)
        form.addWidget(btn_login)

        # Register'a geçiş butonu
        btn_register = QPushButton("Don't have an account? Create one")
        btn_register.setStyleSheet("color: #0078ff; background: transparent; margin-top: 8px;")
        btn_register.clicked.connect(self.go_register)
        form.addWidget(btn_register)

        outer.addStretch()
        outer.addWidget(container)
        outer.addStretch()

        self.setLayout(outer)

    def login(self):
        username = self.username_edit.text().strip()
        if not username:
            QMessageBox.warning(self, "Error", "Kullanıcı adı gir.")
            return

        ok, msg = self.api.login(username)
        if ok:
            QMessageBox.information(self, "Başarılı", msg)
            self.on_login_success()
        else:
            QMessageBox.warning(self, "Error", msg)


# =======================
# REGISTER SAYFASI
# =======================
class RegisterPage(QWidget):
    def __init__(self, api_client, on_register_success, go_login, parent=None):
        super().__init__(parent)
        self.api = api_client
        self.on_register_success = on_register_success
        self.go_login = go_login
        self.selected_image = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background: #ffffff;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        form = QVBoxLayout(container)

        title = QLabel("Create an Account")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 15px;")
        form.addWidget(title)

        # Username
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Username")
        self.username_edit.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        form.addWidget(self.username_edit)

        # Password
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        form.addWidget(self.password_edit)

        # Image select button
        self.image_button = QPushButton("Select Profile Image")
        self.image_button.setStyleSheet("""
            QPushButton {
                background-color: #0078ff;
                color: white;
                padding: 10px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #005fcc;
            }
        """)
        self.image_button.clicked.connect(self.select_image)
        form.addWidget(self.image_button)

        # Register button
        self.register_button = QPushButton("Create Account")
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #1f7e33;
            }
        """)
        self.register_button.clicked.connect(self.register)
        form.addWidget(self.register_button)

        # Back to login
        self.back_btn = QPushButton("Already have an account? Login")
        self.back_btn.setStyleSheet("color: #0078ff; background: transparent;")
        self.back_btn.clicked.connect(self.go_login)
        form.addWidget(self.back_btn)

        layout.addStretch()
        layout.addWidget(container)
        layout.addStretch()

        self.setLayout(layout)


    def select_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        if path:
            self.selected_image = path
            self.image_button.setText("Image Selected")

    def register(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()

        if not username or not password or not self.selected_image:
            QMessageBox.warning(self, "Error", "Tüm alanları doldur ve resim seç.")
            return

        ok, msg = self.api.register(username, password, self.selected_image)
        if ok:
            QMessageBox.information(self, "Success", msg)

            # Kayıt başarılı → Login ekranına dön
            self.on_register_success()   # bu birazdan show_login_page olacak
        else:
            QMessageBox.warning(self, "Error", msg)



# =======================
# CHAT SAYFASI
# =======================
class ChatPage(QWidget):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api = api_client
        self.current_chat_user = None

        self.init_ui()

    def init_ui(self):
        # Genel arka plan rengi
        self.setStyleSheet("background-color: #f0f2f5;")

        main_layout = QHBoxLayout()

        # ============ SOL PANEL (KULLANICI LİSTESİ) ============
        left_panel = QWidget()
        left_panel.setStyleSheet("""
            QWidget {
                background-color: #111b21;
                border-radius: 10px;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel("Chats")
        lbl.setStyleSheet("""
            QLabel {
                color: #e9edef;
                font-weight: bold;
                padding: 10px 12px;
                border-bottom: 1px solid #202c33;
            }
        """)
        left_layout.addWidget(lbl)

        self.user_list = QListWidget()
        self.user_list.itemSelectionChanged.connect(self.on_user_selected)
        self.user_list.setStyleSheet("""
            QListWidget {
                background-color: #111b21;
                color: #e9edef;
                border: none;
            }
            QListWidget::item {
                padding: 8px 10px;
            }
            QListWidget::item:selected {
                background-color: #202c33;
            }
        """)
        left_layout.addWidget(self.user_list)

        self.refresh_users_btn = QPushButton("Refresh")
        self.refresh_users_btn.setStyleSheet("""
            QPushButton {
                background-color: #202c33;
                color: #e9edef;
                padding: 6px 10px;
                border-radius: 6px;
                margin: 8px;
            }
            QPushButton:hover {
                background-color: #2a3942;
            }
        """)
        self.refresh_users_btn.clicked.connect(self.load_users)
        left_layout.addWidget(self.refresh_users_btn)

        main_layout.addWidget(left_panel, 1)

        # ============ SAĞ PANEL (CHAT ALANI) ============
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: #0b141a; border-radius: 10px;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Üst header (Instagram-style gradient)
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff512f, stop:1 #dd2476
                );
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 12, 8)

        self.chat_label = QLabel("No conversation selected")
        self.chat_label.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 15px;
            }
        """)
        header_layout.addWidget(self.chat_label)

        header_layout.addStretch()

        right_layout.addWidget(header)

        # Mesaj alanı
        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        self.chat_view.setStyleSheet("""
            QTextEdit {
                background-color: #0b141a;
                color: #e9edef;
                border: none;
                padding: 10px;
                font-size: 14px;
            }
        """)
        right_layout.addWidget(self.chat_view, 5)

        # Mesaj giriş alanı
        bottom_container = QWidget()
        bottom_container.setStyleSheet("""
            QWidget {
                background-color: #202c33;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(8, 6, 8, 8)

        self.message_edit = QLineEdit()
        self.message_edit.setPlaceholderText("Message...")
        self.message_edit.setStyleSheet("""
            QLineEdit {
                background-color: #2a3942;
                border-radius: 18px;
                padding: 8px 12px;
                color: #e9edef;
                border: 1px solid #202c33;
            }
        """)
        bottom_layout.addWidget(self.message_edit)

        send_btn = QPushButton("Send")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #00a884;
                color: white;
                padding: 8px 16px;
                border-radius: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #029c7b;
            }
        """)
        send_btn.clicked.connect(self.send_message)
        bottom_layout.addWidget(send_btn)

        right_layout.addWidget(bottom_container)

        main_layout.addWidget(right_panel, 3)

        self.setLayout(main_layout)

    # --------- Kullanıcılar ---------
    def load_users(self):
        names, full_data = self.api.get_users()
        self.user_list.clear()
        for user in full_data:
            name = user["username"]
            if name == self.api.current_user:
                continue
            status = "online" if user["online"] else "offline"
            item_text = f"{name} ({status})"
            item = QListWidgetItem(item_text)

            # Online yeşil, offline gri
            if user["online"]:
                item.setForeground(QColor("#25D366"))  # WhatsApp yeşili
            else:
                item.setForeground(QColor("#8696a0"))

            self.user_list.addItem(item)

    def on_user_selected(self):
        items = self.user_list.selectedItems()
        if not items:
            return
        text = items[0].text()   # "c2 (online)" gibi
        name = text.split(" ")[0]
        self.current_chat_user = name
        self.chat_label.setText(f"{name}")

    # --------- Mesaj Gönderme ---------
    def send_message(self):
        if not self.current_chat_user:
            QMessageBox.warning(self, "Error", "Önce listeden bir kullanıcı seç.")
            return

        msg = self.message_edit.text().strip()
        if not msg:
            return

        ok = self.api.send_message(self.current_chat_user, msg)
        if ok:
            # Kendi mesajın: sağda yeşil baloncuk
            bubble = (
                f"<p align='right'>"
                f"<span style='background-color:#005c4b; "
                f"padding:6px 10px; border-radius:10px; "
                f"display:inline-block; color:#e9edef;'>"
                f"{msg}"
                f"</span>"
                f"</p>"
            )
            self.chat_view.append(bubble)
            self.message_edit.clear()
        else:
            QMessageBox.warning(self, "Error", "Mesaj gönderilemedi.")

    # --------- Offline Mesaj Alma (heartbeat ile gelenler) ---------
    def add_incoming_messages(self, messages):
        # messages: [{ "from": "...", "cipher": "base64..." }, ...]
        for m in messages:
            sender = m.get("from")
            cipher_b64 = m.get("cipher", "")
            try:
                raw = base64.b64decode(cipher_b64).decode("utf-8")
                text = raw
            except Exception:
                text = f"(encrypted) {cipher_b64}"

            # Gelen mesaj: solda gri baloncuk
            bubble = (
                f"<p align='left'>"
                f"<span style='background-color:#202c33; "
                f"padding:6px 10px; border-radius:10px; "
                f"display:inline-block; color:#e9edef;'>"
                f"<b>{sender}:</b> {text}"
                f"</span>"
                f"</p>"
            )
            self.chat_view.append(bubble)


# =======================
# MAIN WINDOW
# =======================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.api = ApiClient(base_url="http://127.0.0.1:8000")

        self.setWindowTitle("Şifreli Mesaj Uygulaması")
        self.resize(800, 500)

        self.container = QWidget()
        self.layout = QVBoxLayout()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        # Sayfalar
        self.login_page = LoginPage(
            self.api,
            on_login_success=self.on_login_success,
            go_register=self.show_register_page
        )
        self.register_page = RegisterPage(
            self.api,
            on_register_success=self.show_login_page,
            go_login=self.show_login_page
        )
        self.chat_page = ChatPage(self.api)

        self.current_widget = None

        # Heartbeat timer (otomatik mesaj yenileme)
        self.heartbeat_timer = QTimer(self)
        self.heartbeat_timer.setInterval(4000)  # 4 saniyede bir
        self.heartbeat_timer.timeout.connect(self.send_heartbeat)            
        
        self.show_login_page()


    def clear_layout(self):
        if self.current_widget:
            self.layout.removeWidget(self.current_widget)
            self.current_widget.hide()

    def show_login_page(self):
        self.clear_layout()
        self.current_widget = self.login_page
        self.layout.addWidget(self.login_page)
        self.login_page.show()
        # login ekranına dönünce heartbeat'i durdur
        self.heartbeat_timer.stop()

    def show_register_page(self):
        self.clear_layout()
        self.current_widget = self.register_page
        self.layout.addWidget(self.register_page)
        self.register_page.show()
        self.heartbeat_timer.stop()

    def show_chat_page(self):
        self.clear_layout()
        self.current_widget = self.chat_page
        self.layout.addWidget(self.chat_page)
        self.chat_page.show()
        self.chat_page.load_users()

        # Kullanıcı artık login olduğu için heartbeat'i başlat
        if not self.heartbeat_timer.isActive():
            self.heartbeat_timer.start()

    def on_login_success(self):
        # Hem login'den hem register'dan sonra çağrılacak
        self.show_chat_page()

    def send_heartbeat(self):
        # Sadece bir kullanıcı login ise heartbeat at
        if not self.api.current_user:
            return

        ok, messages = self.api.heartbeat()
        if ok and messages:
            self.chat_page.add_incoming_messages(messages)
            # Kullanıcı listesi de güncellensin
            self.chat_page.load_users()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
