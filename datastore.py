import sys
if sys.implementation.name == "micropython":
    MICROPYTHON = True
else:
    MICROPYTHON = False

import socket


def parse_http_query(q):
    return None


def http_server_loop():
    addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind(addr)
    soc.listen(1)

    while True:
        cl_sock, addr = soc.accept()
        if MICROPYTHON:
            client_stream = cl_sock
        else:
            client_stream = cl_sock.makefile("rwb")

        http_req_line = client_stream.readline()
        http_verb, remain_str = http_req_line.rstrip().split(b" ", 1)
        query, http_version = remain_str.rsplit(b" ", 1)
        while True:
            header = client_stream.readline()
            if header == b"" or header == b"\r\n":
                break

        client_stream.write(b"HTTP/1.0 200 OK\r\nAccess-Control-Allow-Origin: *\r\n\r\n%s" % query)

        client_stream.close()
        if not MICROPYTHON:
            cl_sock.close()


if __name__ == "__main__" and not MICROPYTHON:
    http_server_loop()
