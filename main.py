from temp_measures import get_measurements

print("Executed main.py")

import socket
import time
import gc

import network
from machine import Pin, I2C
import machine

import sdcard
from ntptime import settime
from wifi_config import AP_NAME, AP_PASSWD

led = Pin(2, Pin.OUT)
led(0)

sta_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)
sta_if.active(True)

sta_if.connect(AP_NAME, AP_PASSWD)
while not sta_if.isconnected():
    print("Not connected to wifi")
    time.sleep_ms(500)
led(1)

settime()
gc.collect()






addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind(addr)
print(gc.mem_free())
soc.listen(1)


while True:
    cl, addr = soc.accept()
    print('client connected from', addr)
    cl_file = cl.makefile('rwb', 0)
    led(0)

    while True:
        line = cl_file.readline()
        if not line or line == b'\r\n':
            break

    try:
        res = get_measurements()
        print("RES: %s" % (str(res)))
        
        cl.send(b"HTTP/1.0 200 OK\r\nAccess-Control-Allow-Origin: *\r\n\r\n")
        cl.send(res)
    except:
        cl.send(b"HTTP/1.0 500 OK\r\nAccess-Control-Allow-Origin: *\r\n\r\n")

    led(1)

    cl.close()