import http.server
import socketserver
import threading
import ssl

PORT = 8000

# Замените пути к каталогам на ваши.
# Поместите SSL сертификаты в соответствующую директорию
# И укажите здесь правильный путь.
FOLDER = "/home/container/cdn"
CERT_FILE = "/home/container/modules/ssl/cert.pem"
KEY_FILE = "/home/container/modules/ssl/privkey.pem"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FOLDER, **kwargs)

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError): 
            print("Клиент разорвал соединение")
    
    def send_head(self):
        try:
            return super().send_head()
        except (BrokenPipeError, ConnectionResetError):
            return None
        

# Запуск файлосервера
def run_fileserver():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
        
        httpd.socket = context.wrap_socket(
            httpd.socket,
            server_side=True
        )
        print(f"Файловый сервер запущен на порте {PORT}")
        print(f"Доступ к папке: {FOLDER}")
        httpd.serve_forever()
        

# Если сервер запускается параллельно в другой программе.
# Иначе он не нужен. Вообще.
def start_fileserver():
    thread = threading.Thread(target=run_fileserver)
    thread.daemon = True
    thread.start()
    print("Файловый сервер запущен в фоновом потоке")


if __name__ == "__main__":
    run_fileserver()