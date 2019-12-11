import sys

from temp_measures import get_measurements

if sys.implementation.name == "micropython":
    MICROPYTHON = True
else:
    MICROPYTHON = False
import socket

def proceed_query(q):
    res = b""
    if q.strip() == b"/":
        try:
            res = get_measurements()
        except BaseException as e:
            res = str(e).encode()
    elif q.count(b"/") == 1 and len(q) > 1:
        number = int(q[1:])


    return res


def http_server_loop(led):
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind(addr)
    soc.listen(1)

    while True:
        cl_sock, addr = soc.accept()
        led(0)
        try:
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

            result = proceed_query(query)

            client_stream.write(b"HTTP/1.0 200 OK\r\nAccess-Control-Allow-Origin: *\r\n\r\n")
            client_stream.write(result)
        finally:

            client_stream.close()
            if not MICROPYTHON:
                cl_sock.close()
            led(1)


if __name__ == "__main__" and not MICROPYTHON:
    http_server_loop()
