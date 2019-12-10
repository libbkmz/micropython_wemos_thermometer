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

