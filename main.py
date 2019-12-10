print("Executed main.py")

import time
import gc

import network
from machine import Pin, I2C

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

from datastore import http_server_loop
http_server_loop()