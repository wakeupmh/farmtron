import socketserver
import threading
import logging
import os
import argparse
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from logging.handlers import RotatingFileHandler

parser = argparse.ArgumentParser(description='Honeycomb multi-honeypot')
parser.add_argument('--ftp-port', type=int, default=2121)
parser.add_argument('--mqtt-port', type=int, default=1883)
parser.add_argument('--ssh-port', type=int, default=22)
parser.add_argument('--http-port', type=int, default=80)
parser.add_argument('--log-file', type=str, default=os.getenv('HONEYCOMB_LOG_FILE', 'honeycomb_multi.log'))
args = parser.parse_args()
LOG_FILE = args.log_file

logging.basicConfig(level=logging.INFO)
# Rotating file handler
root = logging.getLogger()
handler = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=3)
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s','%Y-%m-%d %H:%M:%S'))
root.addHandler(handler)

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
            data = self.request.recv(1024)
            # Minimal MQTT CONNECT handling
            if data and data[0] == 0x10:
                # send CONNACK (packet type 0x20)
                self.request.sendall(bytes([0x20,0x02,0x00,0x00]))
                logging.info(f"[MQTT] Sent CONNACK to {client_ip}")
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
            # Read until disconnect
            while True:
                data = self.request.recv(1024)
                if not data:
                    break
                logging.info(f"[SSH] {client_ip} sent: {data}")
        except Exception as e:
            logging.error(f"[SSH] Error: {e}")

# --- HTTP Honeypot ---
class FakeHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        client_ip = self.client_address[0]
        logging.info(f"[HTTP] GET from {client_ip}: {self.path}")
        # Login page
        if self.path == '/login':
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Login</h1><form method='post'><input name='user'><input type='password' name='pass'><button>Login</button></form></body></html>")
            return
        # Status endpoint
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            return
        self.send_response(200)
        self.send_header('Content-type','text/html')
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
    server = socketserver.ThreadingTCPServer(("0.0.0.0", args.ftp_port), FakeFTPHandler)
    logging.info(f"[FTP] Listening on port {args.ftp_port}")
    server.serve_forever()

def start_mqtt():
    server = socketserver.ThreadingTCPServer(("0.0.0.0", args.mqtt_port), FakeMQTTHandler)
    logging.info(f"[MQTT] Listening on port {args.mqtt_port}")
    server.serve_forever()

def start_ssh():
    server = socketserver.ThreadingTCPServer(("0.0.0.0", args.ssh_port), FakeSSHHandler)
    logging.info(f"[SSH] Listening on port {args.ssh_port}")
    server.serve_forever()

def start_http():
    server = HTTPServer(("0.0.0.0", args.http_port), FakeHTTPRequestHandler)
    logging.info(f"[HTTP] Listening on port {args.http_port}")
    server.serve_forever()

if __name__ == "__main__":
    # Start services
    ftp_server = socketserver.ThreadingTCPServer(("0.0.0.0", args.ftp_port), FakeFTPHandler)
    mqtt_server = socketserver.ThreadingTCPServer(("0.0.0.0", args.mqtt_port), FakeMQTTHandler)
    ssh_server = socketserver.ThreadingTCPServer(("0.0.0.0", args.ssh_port), FakeSSHHandler)
    http_server = HTTPServer(("0.0.0.0", args.http_port), FakeHTTPRequestHandler)
    for srv in (ftp_server, mqtt_server, ssh_server, http_server):
        threading.Thread(target=srv.serve_forever, daemon=True).start()
    print(f"Honeycomb multi-honeypot running! (FTP:{args.ftp_port}, MQTT:{args.mqtt_port}, SSH:{args.ssh_port}, HTTP:{args.http_port})")
    print(f"Logs at: {LOG_FILE}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down honeypots...")
        for srv in (ftp_server, mqtt_server, ssh_server, http_server):
            srv.shutdown()
        print("Shutdown complete.")
