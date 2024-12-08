from http.server import BaseHTTPRequestHandler, HTTPServer
from encryption_utils import encrypt_data, decrypt_data
from password_utils import hash_password, verify_password
from rate_limiter import RateLimiter
import sqlite3
import os
import json
import uuid
import datetime

hostName = "localhost"
serverPort = 8080
db_path = os.path.join(os.path.dirname(__file__), 'totally_not_my_privateKeys.db')

rate_limiter = RateLimiter(limit=10, window_seconds=1)  # 10 requests per second

class JWKSHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/register":
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = json.loads(self.rfile.read(content_length))
                username = post_data.get("username")
                email = post_data.get("email")
                password = str(uuid.uuid4())  # Generate a random password

                hashed_password = hash_password(password)

                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                          (username, hashed_password, email))
                conn.commit()

                self.send_response(201)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"password": password}).encode())
            except sqlite3.IntegrityError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Username or email already exists.")
            except Exception as e:
                print(f"Error in /register endpoint: {e}")  # Log the error
                self.send_response(500)
                self.end_headers()
            finally:
                if 'conn' in locals():
                    conn.close()
        elif self.path == "/auth":
            client_ip = self.client_address[0]
            if not rate_limiter.is_allowed(client_ip):
                self.send_response(429)
                self.end_headers()
                self.wfile.write(b"Too Many Requests")
                return

            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = json.loads(self.rfile.read(content_length))
                username = post_data.get("username")
                password = post_data.get("password")

                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                c.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
                user = c.fetchone()
                if user and verify_password(password, user[1]):
                    user_id = user[0]
                    c.execute("INSERT INTO auth_logs (request_ip, user_id) VALUES (?, ?)",
                              (client_ip, user_id))
                    conn.commit()
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"Authentication successful.")
                else:
                    self.send_response(401)
                    self.end_headers()
                    self.wfile.write(b"Authentication failed.")
            except Exception as e:
                print(f"Error in /auth endpoint: {e}")  # Log the error
                self.send_response(500)
                self.end_headers()
            finally:
                if 'conn' in locals():
                    conn.close()
        else:
            self.send_response(405)
            self.end_headers()

    def do_GET(self):
        self.send_response(405)
        self.end_headers()

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), JWKSHandler)
    print(f"Server started on http://{hostName}:{serverPort}")
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print("Server stopped.")
