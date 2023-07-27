import socket
import sys


def check_header(key, headers):
    if key in headers:
        return
    else:
        headers[key] = ""
    return headers


def standarize_header(header):
    keys = [
        'SERVER_PROTOCOL',
        'REQUEST_METHOD',
        'PATH_INFO',
        'Host',
        'Connection',
        'Cache-Control',
        'sec-ch-ua',
        'sec-ch-ua-platform',
        'Upgrade-Insecure-Requests',
        'User-Agent',
        'Accept',
        'Sec-Fetch-Site',
        'Sec-Fetch-Mode',
        'Sec-Fetch-User',
        'Sec-Fetch-Dest',
        'Accept-Encoding',
        'Accept-Language',
        'Cookie',
        'Referer',
    ]
    for key in keys:
        check_header(key, header)
    return header


def parse_header(request_str):
    if request_str != "":
        lines = request_str.strip().split('\n')
        headers = {}
        method, path, http_version = lines[0].split()
        headers = {'REQUEST_METHOD': method,
                   'PATH_INFO': path, 'SERVER_PROTOCOL': http_version}
        for line in lines[1:]:
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
        return headers
    return {}


class WSGIServer:
    def __init__(self, host, port, app):
        self.host = host
        self.port = port
        self.app = app

    def handle_request(self, client_socket):
        request_data = b''
        while True:
            chunk = client_socket.recv(1024)
            if not chunk:
                break
            request_data += chunk
            if b'\r\n\r\n' in request_data:
                break

        request_text = request_data.decode()
        header = parse_header(request_text)
        _header = standarize_header(header)
        path, query = '/', ''
        if _header:
            if '?' in _header['PATH_INFO']:
                path, query = _header['PATH_INFO'].split('?', 1)
            else:
                path, query = header['PATH_INFO'], ''
        wsgi_env = {
            'SERVER_NAME': socket.getfqdn(self.host),
            'GATEWAY_INTERFACE': 'CGI/1.1',
            'REMOTE_HOST': str(self.host),
            'SERVER_PORT': str(self.port),
            'REQUEST_METHOD': _header['REQUEST_METHOD'],
            'CONTENT_LENGTH': '',
            'SCRIPT_NAME': '',
            'SERVER_SOFTWARE': 'WSGIServer/1.0',
            'SERVER_PROTOCOL': _header['SERVER_PROTOCOL'],
            'PATH_INFO': path,
            'QUERY_STRING': query,
            'CONTENT_TYPE': 'text/plain',
            'HTTP_HOST': _header['Host'],
            'HTTP_CONNECTION': _header['Connection'],
            'HTTP_CACHE_CONTROL': _header['Cache-Control'],
            'HTTP_SEC_CH_UA': _header['sec-ch-ua'], 'HTTP_SEC_CH_UA_MOBILE': '?0',
            'HTTP_SEC_CH_UA_PLATFORM': _header['sec-ch-ua-platform'],
            'HTTP_UPGRADE_INSECURE_REQUESTS': _header['Upgrade-Insecure-Requests'],
            'HTTP_USER_AGENT': _header['User-Agent'],
            'HTTP_ACCEPT': _header['Accept'],
            'HTTP_SEC_FETCH_SITE': _header['Sec-Fetch-Site'],
            'HTTP_SEC_FETCH_MODE': _header['Sec-Fetch-Mode'],
            'HTTP_SEC_FETCH_USER': _header['Sec-Fetch-User'],
            'HTTP_SEC_FETCH_DEST': _header['Sec-Fetch-Dest'],
            'HTTP_ACCEPT_ENCODING': _header['Accept-Encoding'],
            'HTTP_ACCEPT_LANGUAGE': _header['Accept-Language'],
            'COOKIE': _header['Cookie'],
            'REFERER': _header['Referer'],
            'wsgi.input': request_data,
            'wsgi.errors': sys.stderr,
            'wsgi.version': (1, 0),
            'wsgi.async': False,
            'wsgi.run_once': False,
            'wsgi.url_scheme': 'http',
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
        }
        response = self.app(wsgi_env, self.start_response)
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
