import socket
import sys
import pickle


def parse_header(request_str):
    lines = request_str.strip().split('\n')
    try:
        method, path, http_version = lines[0].split()
    except:
        method, path, http_version = "GET", "/", "HTTP/1.1"
    headers = {'REQUEST_METHOD': method,
               'PATH_INFO': path, 'SERVER_PROTOCOL': http_version}
    for line in lines[1:]:
        key, value = line.split(':', 1)
        headers[key.strip()] = value.strip()
    # cookies = {}
    # cookie_str = headers.get('Cookie', '')
    # if cookie_str:
    #     cookie_items = cookie_str.split(';')
    #     for item in cookie_items:
    #         key, value = item.split('=')
    #         cookies[key.strip()] = value.strip()
    return headers


class WSGIServer:
    def __init__(self, host, port, app):
        self.host = host
        self.port = port
        self.app = app

    def handle_request(self, client_socket):
        request_data = client_socket.recv(1024)
        request_text = request_data.decode()
        header = parse_header(request_text)
        print("[HANDLE_REQUEST]\n", header['PATH_INFO'])
        environ = {
            'REQUEST_METHOD': header['REQUEST_METHOD'],
            'PATH_INFO': header['PATH_INFO'],
            'QUERY_STRING': '',
            'SERVER_PROTOCOL': header['SERVER_PROTOCOL'],
            'SERVER_NAME': self.host,
            'SERVER_PORT': str(self.port),
            'wsgi.input': request_data,
            'wsgi.errors': sys.stderr,
            'wsgi.version': (1, 0),
            'wsgi.async': False,
            'wsgi.run_once': False,
            'wsgi.url_scheme': 'http',
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
        }
        response = self.app(environ, self.start_response)
        try:
            self.send_response(client_socket, response)
        except ConnectionAbortedError:
            print("Client closed the connection unexpectedly.")
        finally:
            client_socket.close()

    def start_response(self, status, response_headers):
        self.http_version = 'HTTP/1.1'
        self.status = status
        self.response_headers = response_headers

    def send_response(self, client_socket, response):
        response_headers = [f"{key}: {value}" for key,
                            value in self.response_headers]
        response_headers.append("Connection: keep-alive")
        response_text = "\r\n".join(
            [self.http_version + " " + self.status] + response_headers + ["", ""])
        client_socket.sendall(response_text.encode())
        for data in response:
            client_socket.send(data)
        client_socket.close()

    def serve_forever(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        # server_socket.listen()
        server_socket.listen(5)

        try:
            while True:
                conn, addr = server_socket.accept()
                self.handle_request(conn)
        except KeyboardInterrupt:
            print("Server stopped by KeyboardInterrupt (Ctrl+C)")
        finally:
            server_socket.close()
