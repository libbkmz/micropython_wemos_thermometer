print("Executed main.py")

import network
import esp
import time
import dht12
import sht30
from machine import Pin, I2C
import socket
import json
from wifi_config import AP_NAME, AP_PASSWD

ITERATION_SLEEP_MS = 2500


esp.sleep_type(esp.SLEEP_LIGHT)

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
# webrepl.start()
led(1)

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind(addr)
soc.listen(1)


i2c = I2C(scl=Pin(5), sda=Pin(4))
dht_sens = dht12.DHT12(i2c)
sht_sens = sht30.SHT30(i2c)

def get_measurements():
    dht_sens.measure()
    sht_temp, sht_hum = sht_sens.measure()
    out = {
        "sht": {
            "temp": sht_temp,
            "hum": sht_hum,
        },
        "dht": {
            "temp": dht_sens.temperature(),
            "hum": dht_sens.humidity(),
        }
    }
    return json.dumps(out)


while True:
    cl, addr = soc.accept()
    print('client connected from', addr)
    cl_file = cl.makefile('rwb', 0)
    led(0)

    data = cl_file.read(1)
    print(data)
    if data == b"\x01":
        print("get_measurements")
        res = get_measurements()
    else:
        res = ""
        print(data)
        cl.close()
        led(1)
        continue
    
    print("RES: %s" % (str(res)))
    
    cl.send(res)
    led(1)

    cl.close()

# while True:
#     led(0)
#     try:
#         dht_sens.measure()
#         sht_temp, sht_hum = sht_sens.measure()
#     except Exception as e:
#         print(e)
#         time.sleep_ms(ITERATION_SLEEP_MS)
#         continue

#     print("DHT: %.1fC %.1fH" % (dht_sens.temperature(), dht_sens.humidity()))
#     print("SHT: %.1fC %.1fH" % (sht_temp, sht_hum))
#     # print()

#     led(1)
#     time.sleep_ms(ITERATION_SLEEP_MS)
