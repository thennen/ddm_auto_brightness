# this is supposed to set the monitor to a brightness as a function of time
# just put it in the windows scheduler

import os
from math import cos, pi
from datetime import datetime

# is a sin function a good idea?
maxbrightness = 70
minbrightness = 10
now = datetime.now()

nowDec = now.hour + now.minute/60

maxtime = 12

brightness = int(round(minbrightness + (maxbrightness - minbrightness) * (1 + cos((nowDec - maxtime)*2*pi/24))/2))

os.system(fr'"C:\Program Files (x86)\Dell\Dell Display Manager\ddm.exe" /SetBrightnessLevel {brightness}')
