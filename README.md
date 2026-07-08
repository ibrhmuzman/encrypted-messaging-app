# Secure Messaging System with Steganography

A secure client-server messaging application developed in Python. The system combines **LSB (Least Significant Bit) steganography** and **DES encryption** to provide secure user registration and message transmission.

## Features

- User registration with username, password and profile image
- Password embedding into an image using LSB steganography
- Password extraction on the server during registration
- Secure message transmission using DES encryption
- Client-server architecture
- User list management
- Offline message storage and delivery
- Simple and user-friendly graphical interface

## How It Works

### User Registration

1. The user enters a username and password.
2. A profile image is selected.
3. The password is embedded into the image using the LSB steganography algorithm.
4. The generated image is sent to the server.
5. The server extracts the hidden password and associates it with the corresponding user.

### Secure Messaging

1. The sender selects a recipient.
2. The message is encrypted using the sender's DES key.
3. The encrypted message is sent to the server.
4. The server decrypts the message using the sender's key.
5. The message is encrypted again using the recipient's key.
6. The encrypted message is stored until the recipient becomes available.
7. The recipient decrypts the message using their own key.

## Technologies Used

- Python
- PyQt5
- FastAPI
- Pillow
- PyCryptodome
- LSB Steganography
- DES Encryption

## Project Structure

```
project/
│
├── client/
│   ├── ui/
│   ├── register/
│   ├── messaging/
│   └── api/
│
├── server/
│   ├── routes/
│   ├── database/
│   ├── message_service/
│   └── user_service/
│
├── security/
│   ├── des.py
│   ├── stegano.py
│   └── utils.py
│
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/project-name.git
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the server:

```bash
python server.py
```

Run the client:

```bash
python client.py
```

## Security

- Passwords are hidden inside images using the LSB steganography algorithm.
- Messages are encrypted using the DES symmetric encryption algorithm.
- The server re-encrypts messages using the recipient's key before storing them.
- Offline messages remain encrypted until they are delivered to the recipient.

## License

This project was developed for educational purposes.
