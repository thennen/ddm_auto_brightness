# this is supposed to set the monitor to a brightness as a function of time
# just put it in the windows scheduler

import os
from math import sin, cos, pi
from datetime import datetime
from dateutil import tz


maxbrightness = 80
minbrightness = 5
now = datetime.now(tz.tz.tzlocal())
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
except:
    # old way
    nowDec = now.hour + now.minute/60
    maxtime = 12
    # is a sin function a good idea?
    brightness = int(round(minbrightness + (maxbrightness - minbrightness) * (1 + cos((nowDec - maxtime)*2*pi/24))/2))

bypass = False
if not bypass:
    os.system(fr'"C:\Program Files (x86)\Dell\Dell Display Manager\ddm.exe" /SetBrightnessLevel {brightness}')
