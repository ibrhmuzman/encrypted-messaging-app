import sys
import base64
import requests
import sys
import os


from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QMessageBox
)

# ---- security imports ----
from stegano_utils import stegano_embed, stegano_extract
from des_utils import generate_random_key



# ---- api client ----
from client import ApiClient




class RegisterLoginApp(QWidget):
    def __init__(self):
        super().__init__()
        self.api = ApiClient()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Secure Chat - Phase 2.1")
        self.setGeometry(300, 300, 350, 250)

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.image_path = None
        self.select_btn = QPushButton("Select Profile Image")
        self.select_btn.clicked.connect(self.select_image)
        layout.addWidget(self.select_btn)

        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.register)
        layout.addWidget(self.register_btn)

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)
    


    # -------------------------
    # IMAGE PICKER
    # -------------------------
    def select_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg)"
        )
        if path:
            self.image_path = path
            self.select_btn.setText("Image Selected")

    # -------------------------
    # REGISTER (FAZ 2.1)
    # -------------------------
    def register(self):
        username = self.username_input.text().strip()
        if not username or not self.image_path:
            QMessageBox.warning(self, "Error", "Username and image required")
            return

        # 1) Key üret
        key = generate_random_key()

        # 2) Image oku
        with open(self.image_path, "rb") as f:
            image_bytes = f.read()

        # 3) Key image'a göm
        embedded_image = stegano_embed(image_bytes, key)

        # 4) Embedded image → base64
        img_b64 = base64.b64encode(embedded_image).decode()

        # 5) Server'a GÖMÜLÜ IMAGE gönder
        ok, msg = self.api.register(username, img_b64)

        if ok:
            QMessageBox.information(self, "Success", "Registered successfully")
        else:
            QMessageBox.warning(self, "Error", msg)


    # -------------------------
    # LOGIN (FAZ 2.1)
    # -------------------------
    def login(self):
        username = self.username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Error", "Username required")
            return

        ok, msg = self.api.login(username)
        if not ok:
            QMessageBox.warning(self, "Error", msg)
            return

        try:
            image_bytes = self.api.fetch_profile_image(username)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
            return

        key = stegano_extract(image_bytes)
        del image_bytes

        self.api.session_key = key


        QMessageBox.information(
            self, "Login successful",
            "Session key extracted and loaded into RAM"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = RegisterLoginApp()
    w.show()
    sys.exit(app.exec_())
