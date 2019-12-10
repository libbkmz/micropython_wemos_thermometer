import json

from machine import Pin, I2C, SPI, Timer
import sdcard

import dht12
import sht30

i2c = I2C(scl=Pin(5), sda=Pin(4))
dht_sens = dht12.DHT12(i2c)
sht_sens = sht30.SHT30(i2c)

sd = sdcard.SDCard(SPI(1), Pin(15))
buffer_4096 = bytearray(4096)
pointer = 0


def timer_periodic_callback(t):
    pass


timer = Timer(-1)
timer.init(period=2500, mode=Timer.PERIODIC, callback=timer_periodic_callback)


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


