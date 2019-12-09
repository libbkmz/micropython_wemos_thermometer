print("Executed main.py")

import network
import esp
import time
import dht12
import sht30
from machine import Pin, I2C, SPI
import sdcard, os
import socket
import json
from wifi_config import AP_NAME, AP_PASSWD


led = Pin(2, Pin.OUT)
led(0)

sta_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)
sta_if.active(True)

sta_if.connect(AP_NAME, AP_PASSWD)
while not sta_if.isconnected():
    print ("Not connected to wifi")
    time.sleep_ms(500)
led(1)

from ntptime import settime
settime()
gc.collect()


sd = sdcard.SDCard(machine.SPI(1), machine.Pin(15)) 
buffer_4096 = bytearray(4096)
pointer = 0

i2c = I2C(scl=Pin(5), sda=Pin(4))
dht_sens = dht12.DHT12(i2c)
sht_sens = sht30.SHT30(i2c)

def get_measurements():
    dht_sens.measure()
    sht_temp, sht_hum = sht_sens.measure()
    out = {
            "sht_temp": sht_temp,
            "sht_hum": sht_hum,
            "dht_temp": dht_sens.temperature(),
            "dht_hum": dht_sens.humidity(),
    }
    return json.dumps(out)

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