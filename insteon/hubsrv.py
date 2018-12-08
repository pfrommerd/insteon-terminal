from http.server import BaseHTTPRequestHandler, HTTPServer

import binascii
import threading

def make_handler(srv):
    class HubHandler(BaseHTTPRequestHandler):
        def do_HEAD(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_GET(self):
            # Parse the path to either
            if self.path == '/buffstatus.xml':
                self.handle_buffer_request()
            elif self.path == '/1?XB=M=1':
                self.handle_buffer_clear()
            elif self.path.startswith('/3?') and self.path.endswith('=I=3'):
                self.handle_write_request(self.path[3:len(self.path) - 4])
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.send_text('Not found!')

        def handle_buffer_request(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/xml')
            self.end_headers()
            data = srv._buffer
            hexstr = binascii.hexlify(data)
            self.send_text('buffer: ' + hexstr)
        
        def handle_buffer_clear(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/xml')
            self.end_headers()
            srv.clear()
            self.send_text('buffer cleared!')

        def handle_write_request(self, hex_data):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            try:
                data = binascii.unhexlify(hex_data)
                self.send_text('writing: ' + hex_data)
            except:
                self.send_text('error!')
                return

        def send_text(self, text):
            self.wfile.write(bytes(text, 'UTF-8'))
    return HubHandler

class HubServer:
    def __init__(self, io_conn, port, bufferlen):
        self._io_conn = io_conn
        self._port = port
        self._handler = make_handler(self)

        self._buffer_lock = threading.Lock()
        self._buffer = bytearray(bufferlen)
        self._buffer_pos = 0

    def run(self):
        self._io_conn.open()

        # Start the http server
        self.run_http_server()

        self._io_conn.close()

    def run_http_server(self):
        httpd = HTTPServer(("", port), self._handler)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()

    def get_buffer(self):
        with self.buffer_lock:
            return bytearray(self._buffer)

    def clear(self):
        with self.buffer_lock:
            self._buffer = bytearray(len(self.buffer))
            self._buffer_pos = 0

if __name__ == '__main__':
    port = 8008
    print('Server started on port {}'.format(port))
