# this is supposed to set the monitor to a brightness as a function of time
# just put it in the windows scheduler and tell it to run every 15 minutes

import os
from math import sin, cos, pi
from datetime import datetime
from dateutil import tz
import time

import logging

logging.basicConfig(filename="autodisplaybrightness.log", level=logging.INFO)

maxbrightness = 100
minbrightness = 5
now = datetime.now(tz.tz.tzlocal())

try:
    # Fancy way that reads room brightness from arduino
    # Just a voltage divider
    # 100 mV in the sun
    # ~2 V daytime normal light
    # 3.3 V in the dark
    import serial
    s = serial.Serial('COM6')
    # Wait for some samples
    time.sleep(5)
    vsamples = [float(v) for v in s.read_all().decode().split('\r\n') if v]
    s.close()
    vmean = sum(vsamples) / len(vsamples)
    vnorm = 1 - max(0, (vmean - 0.1) / 3.2)
    # Maybe a power law works
    exponent = .2
    brightness = minbrightness + vnorm**exponent * (maxbrightness - minbrightness)
    brightness = int(round(brightness))
    way = 'LDR'
except:
    try:
        from suntime import Sun
        sun = Sun(50.7753, 6.0839)
        rise = sun.get_local_sunrise_time()
        set = sun.get_local_sunset_time()
        dayfrac = (now - rise) / (set - rise)
        dayfrac = max(dayfrac, 0)
        dayfrac = min(dayfrac, 1)
        # always at minbrightness while sun is set
        brightness = int(round(minbrightness + (maxbrightness - minbrightness) * sin(dayfrac*pi)))
        way = 'suntime'
    except:
        # old way
        nowDec = now.hour + now.minute/60
        maxtime = 12
        # is a sine function a good idea?
        brightness = int(round(minbrightness + (maxbrightness - minbrightness) * (1 + cos((nowDec - maxtime)*2*pi/24))/2))
        way = 'sin'

bypass = False
if not bypass:
    os.system(fr'"C:\Program Files (x86)\Dell\Dell Display Manager\ddm.exe" /SetBrightnessLevel {brightness}')
    nowstr = now.strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f'{nowstr}\t{way}\t{brightness}')
