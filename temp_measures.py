import json
import time
import struct

from machine import Pin, I2C, SPI, Timer
import sdcard

import dht12
import sht30

binary_struct = b"<I4f"
binary_struct_len = struct.calcsize(binary_struct)

i2c = I2C(scl=Pin(5), sda=Pin(4))
dht_sens = dht12.DHT12(i2c)
sht_sens = sht30.SHT30(i2c)

sd = sdcard.SDCard(SPI(1), Pin(15))
assert sd.csd_version == 2
buffer_4096 = bytearray(512)
pointer = 0
buffer_cursor = 0  # in lba size units
SD_LBA_SIZE = const(512)

last_measurements = None
last_measurements_time = 0
measurements_store_time_limit_sec = 2.5


def _get_measures():
    global last_measurements_time, last_measurements
    if time.time() < last_measurements_time + measurements_store_time_limit_sec:
        return last_measurements

    dht_sens.measure()
    sht_temp, sht_hum = sht_sens.measure()
    out = {
        "now": time.time(),
        "sht_temp": sht_temp,
        "sht_hum": sht_hum,
        "dht_temp": dht_sens.temperature(),
        "dht_hum": dht_sens.humidity(),
    }
    last_measurements = out
    last_measurements_time = out["now"]
    return out


def flush_buffer():
    global buffer_cursor, pointer, buffer_4096

    print(buffer_4096)
    sd.writeblocks(buffer_cursor, buffer_4096)
    print("written data to SD card")

    buffer_cursor += (len(buffer_4096) // SD_LBA_SIZE)
    pointer = 0

    buffer_4096 = bytearray(len(buffer_4096))


def save_dict_to_buffer(d):
    global pointer

    if pointer + binary_struct_len > len(buffer_4096):
        flush_buffer()

    assert pointer + binary_struct_len <= len(buffer_4096)

    struct.pack_into(binary_struct, buffer_4096, pointer, d["now"], d["dht_hum"], d["sht_hum"], d["dht_temp"], d["sht_temp"])
    pointer += binary_struct_len


def get_measurements():
    return json.dumps(_get_measures())


def timer_periodic_callback(t):
    d = _get_measures()
    save_dict_to_buffer(d)
    print("Callback, '%s'" % str(last_measurements))


timer = Timer(-1)
timer.init(period=2000, mode=Timer.PERIODIC, callback=timer_periodic_callback)
