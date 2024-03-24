from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote_plus
from datetime import datetime
from threading import Thread
from pathlib import Path
import urllib.parse
import mimetypes
import socket
import json


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # print(f"{self.headers.get('Content-Length') = }")
        data = self.rfile.read(int(self.headers.get('Content-Length')))
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data, ('', 5000))
        client_socket.close()
        # print(f"{unquote_plus(data.decode()) = }")
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
        # print(f"{mt = }")
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
    list_data = []
    list_data.append(dict_data)
    formatted_dict = {}
    for _, data in enumerate(list_data):
        timestamp = datetime.now()
        formatted_dict.update({str(timestamp):data})

    with open("storage/data.json", "a", encoding="utf-8") as f:
        json.dump(formatted_dict, f, indent=4, ensure_ascii=False)
        f.write(",\n")

def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

def socket_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))

    try:
        while True:
            msg, address = server_socket.recvfrom(1024)
            print(f"Socket received {address}: {msg}")

            save_to_json(msg)
    except KeyboardInterrupt:
        pass
    finally:
        server_socket.close()



if __name__ == '__main__':
    server = Thread(target=run, args=(HTTPServer, HttpHandler))
    server.start()

    server_socket = Thread(target=socket_server, args=('', 5000))
    server_socket.start()
