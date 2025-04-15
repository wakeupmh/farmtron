import socketserver
import threading
import logging
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

LOG_FILE = os.getenv('HONEYCOMB_LOG_FILE', 'honeycomb_multi.log')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- FTP Honeypot ---
class FakeFTPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        client_ip = self.client_address[0]
        logging.info(f"[FTP] Connection from {client_ip}")
        try:
            self.request.sendall(b"220 Fake FTP Service Ready\r\n")
            while True:
                data = self.request.recv(1024)
                if not data:
                    break
                cmd = data.decode(errors='ignore').strip()
                logging.info(f"[FTP] {client_ip} > {cmd}")
                if cmd.upper().startswith('USER'):
                    self.request.sendall(b"331 Username OK, need password\r\n")
                elif cmd.upper().startswith('PASS'):
                    self.request.sendall(b"530 Login incorrect\r\n")
                elif cmd.upper() == 'QUIT':
                    self.request.sendall(b"221 Goodbye.\r\n")
                    break
                else:
                    self.request.sendall(b"502 Command not implemented\r\n")
        except Exception as e:
            logging.error(f"[FTP] Error: {e}")

# --- MQTT Honeypot ---
class FakeMQTTHandler(socketserver.BaseRequestHandler):
    def handle(self):
        client_ip = self.client_address[0]
        logging.info(f"[MQTT] Connection from {client_ip}")
        try:
            # Just accept connection, log, and close
            self.request.sendall(b"MQTT\n")
            data = self.request.recv(1024)
            logging.info(f"[MQTT] {client_ip} sent: {data}")
        except Exception as e:
            logging.error(f"[MQTT] Error: {e}")

# --- SSH Honeypot ---
class FakeSSHHandler(socketserver.BaseRequestHandler):
    def handle(self):
        client_ip = self.client_address[0]
        logging.info(f"[SSH] Connection from {client_ip}")
        try:
            self.request.sendall(b"SSH-2.0-OpenSSH_7.9p1 Debian-10\r\n")
            data = self.request.recv(1024)
            logging.info(f"[SSH] {client_ip} sent: {data}")
        except Exception as e:
            logging.error(f"[SSH] Error: {e}")

# --- HTTP Honeypot ---
class FakeHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        client_ip = self.client_address[0]
        logging.info(f"[HTTP] GET from {client_ip}: {self.path}")
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<html><body><h1>IoT Device Admin Panel</h1><p>Firmware v1.0.0</p></body></html>")
    def do_POST(self):
        client_ip = self.client_address[0]
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        logging.info(f"[HTTP] POST from {client_ip}: {self.path}, Data: {post_data}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        return  # Silence default HTTP server logging

# --- Start servers in threads ---
def start_ftp():
    server = socketserver.ThreadingTCPServer(("0.0.0.0", 2121), FakeFTPHandler)
    logging.info("[FTP] Listening on port 2121")
    server.serve_forever()

def start_mqtt():
    server = socketserver.ThreadingTCPServer(("0.0.0.0", 1883), FakeMQTTHandler)
    logging.info("[MQTT] Listening on port 1883")
    server.serve_forever()

def start_ssh():
    server = socketserver.ThreadingTCPServer(("0.0.0.0", 22), FakeSSHHandler)
    logging.info("[SSH] Listening on port 22")
    server.serve_forever()

def start_http():
    server = HTTPServer(("0.0.0.0", 80), FakeHTTPRequestHandler)
    logging.info("[HTTP] Listening on port 80")
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=start_ftp, daemon=True).start()
    threading.Thread(target=start_mqtt, daemon=True).start()
    threading.Thread(target=start_ssh, daemon=True).start()
    threading.Thread(target=start_http, daemon=True).start()
    print("Honeycomb multi-honeypot running! (FTP:2121, MQTT:1883, SSH:22, HTTP:80)")
    print(f"Logs at: {LOG_FILE}")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Shutting down honeypots...")
