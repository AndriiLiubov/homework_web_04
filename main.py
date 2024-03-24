import socket
import json
from datetime import datetime
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote_plus
from pathlib import Path
import urllib.parse
import mimetypes

class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers.get('Content-Length')))
        save_to_json(data) 
        print(f"{unquote_plus(data.decode()) = }")
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            file_path = Path(pr_url.path[1:])
            if file_path.exists():
                self.send_static(str(file_path))
            else:
                self.send_html_file("error.html", 404)

    def send_static(self, static_filename):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header('Content-type', mt[0])
        else:
            self.send_header('Content-type', 'text/plain')
        self.end_headers()
        with open(static_filename, 'rb') as f:
            self.wfile.write(f.read())

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

def save_to_json(raw_data):
    data = unquote_plus(raw_data.decode())
    dict_data = {key: value for key, value in [el.split("=") for el in data.split("&")]}
    list_data = [dict_data]
    formatted_dict = {}
    for _, data in enumerate(list_data):
        timestamp = datetime.now()
        formatted_dict.update({str(timestamp): data})

    with open("storage/data.json", "a", encoding="utf-8") as f:
        json.dump(formatted_dict, f, indent=4, ensure_ascii=False)
        f.write(",\n")

def run_http_server():
    server_address = ('', 3000)
    http = HTTPServer(server_address, HttpHandler)
    http.serve_forever()

def run_socket_server():
    host = socket.gethostname()
    port = 5000

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(10)
    conn, address = server_socket.accept()
    print(f'Connection from {address}')
    while True:
        data = conn.recv(100).decode()

        if not data:
            break
        save_to_json(data)

    conn.close()

if __name__ == '__main__':
    http_server = Thread(target=run_http_server)
    http_server.start()

    socket_server = Thread(target=run_socket_server)
    socket_server.start()