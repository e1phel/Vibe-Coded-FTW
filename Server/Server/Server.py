import socket
import threading
import json
import os
import re
import hashlib
import secrets

HOST = "0.0.0.0"
PORT = 5050
USERS_FILE = "users.json"

# Extend this list however you like
BAD_WORDS = ["fuck", "shit", "bitch", "asshole", "bastard", "damn", "crap", "dick", "piss"]
BAD_RE = re.compile(r"\b(" + "|".join(BAD_WORDS) + r")\b", re.IGNORECASE)

clients = {}                    # username -> connection
clients_lock = threading.Lock()
users_lock = threading.Lock()


def send(conn, text):
    try:
        conn.sendall((text + "\n").encode("utf-8"))
    except OSError:
        pass


def broadcast(text, exclude=None):
    with clients_lock:
        for name, c in clients.items():
            if name != exclude:
                send(c, text)


# ---------- user storage (salted + hashed passwords) ----------
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)


def hash_pw(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 100_000).hex()


def authenticate(conn, f):
    """Returns the username on success, None on failure."""
    send(conn, "AUTH_REQUIRED")
    for _ in range(3):                       # 3 attempts
        line = f.readline()
        if not line:
            return None
        parts = line.strip().split("|", 2)   # ACTION|username|password
        if len(parts) != 3:
            send(conn, "ERR Bad request")
            continue
        action, user, pw = parts

        with users_lock:
            users = load_users()

            if action == "REGISTER":
                if not (3 <= len(user) <= 20 and user.isalnum()):
                    send(conn, "ERR Username must be 3-20 letters/numbers")
                    continue
                if BAD_RE.search(user):
                    send(conn, "ERR Inappropriate username")
                    continue
                if len(pw) < 4:
                    send(conn, "ERR Password must be at least 4 characters")
                    continue
                if user in users:
                    send(conn, "ERR Username already taken")
                    continue
                salt = secrets.token_hex(16)
                users[user] = {"salt": salt, "hash": hash_pw(pw, salt)}
                save_users(users)

            elif action == "LOGIN":
                rec = users.get(user)
                if not rec or hash_pw(pw, rec["salt"]) != rec["hash"]:
                    send(conn, "ERR Invalid username or password")
                    continue
            else:
                send(conn, "ERR Unknown action")
                continue

        with clients_lock:
            if user in clients:
                send(conn, "ERR That user is already logged in")
                continue

        send(conn, "OK Welcome, " + user + "! Type 'disconnect1122' to leave.")
        return user

    send(conn, "ERR Too many failed attempts")
    return None


def handle_client(conn, addr):
    print(f"[+] Connected: {addr}")
    f = conn.makefile("r", encoding="utf-8")
    username = None
    kicked = False
    try:
        username = authenticate(conn, f)
        if not username:
            return

        with clients_lock:
            clients[username] = conn
        print(f"[*] {username} logged in")
        broadcast(f"*** {username} joined the chat ***", exclude=username)

        for line in f:
            msg = line.strip()
            if not msg:
                continue

            if msg == "disconnect1122":
                send(conn, "Disconnecting. Bye!")
                break

            if BAD_RE.search(msg):
                send(conn, "Inappropriate word detected. You have been kicked.")
                broadcast(f"*** {username} was kicked for inappropriate language ***", exclude=username)
                print(f"[!] Kicked {username} for profanity")
                kicked = True
                break

            print(f"[{username}] {msg}")
            broadcast(f"{username}: {msg}", exclude=username)
    except (ConnectionError, OSError):
        pass
    finally:
        if username:
            with clients_lock:
                clients.pop(username, None)
            if not kicked:
                broadcast(f"*** {username} left the chat ***")
        try:
            conn.close()
        except OSError:
            pass
        print(f"[-] Disconnected: {addr}")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Chat server running on {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()