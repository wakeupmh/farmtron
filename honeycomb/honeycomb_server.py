import socketserver
import logging
import os
from datetime import datetime

# Configuração do log
LOG_FILE = os.getenv('HONEYCOMB_LOG_FILE', 'honeycomb_ftp.log')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

FAKE_BANNER = b"220 Fake FTP Service Ready\r\n"

class FakeFTPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        client_ip = self.client_address[0]
        logging.info(f"Conexão FTP de {client_ip}")
        try:
            self.request.sendall(FAKE_BANNER)
            while True:
                data = self.request.recv(1024)
                if not data:
                    break
                cmd = data.decode(errors='ignore').strip()
                logging.info(f"{client_ip} > {cmd}")
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
            logging.error(f"Erro na conexão FTP fake: {e}")

if __name__ == "__main__":
    server = socketserver.ThreadingTCPServer(("0.0.0.0", 2121), FakeFTPHandler)
    logging.info("Fake FTP server escutando na porta 2121")
    print("Honeycomb FTP rodando na porta 2121!")
    print(f"Logs em: {LOG_FILE}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Encerrando honeycomb FTP...")
