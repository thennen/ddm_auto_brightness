# this is supposed to set the monitor to a brightness as a function of time
# just put it in the windows scheduler and tell it to run every 15 minutes

import os
from math import sin, cos, pi
from datetime import datetime
from dateutil import tz
import time

import logging

logging.basicConfig(filename="autodisplaybrightness.log", level=logging.INFO)

maxbrightness = 75
minbrightness = 15
now = datetime.now(tz.tz.tzlocal())

bypass = False

# New version
ddm2_fp = r"C:\Program Files\Dell\Dell Display Manager 2\DDM.exe"
# Old version needed e.g. for U2415b
ddm_fp = r"C:\Program Files (x86)\Dell\Dell Display Manager\ddm.exe"


def set_brightness(brightness, log=True):
    brightness = int(round(brightness))
    if os.path.isfile(ddm_fp):
        os.system(fr'"{ddm_fp}" /SetBrightnessLevel {brightness}')
    if os.path.isfile(ddm2_fp):
        os.system(fr'"{ddm2_fp}" /WriteBrightnessLevel {brightness}')

    nowstr = now.strftime('%Y-%m-%d %H:%M:%S')
    logstring = f'{nowstr}\t{way}\t{brightness}'
    if log:
        logging.info(logstring)
    print(logstring)
    return brightness

def get_brightness():
    '''
    DDM doesn't let you do this for whatever reason; see these funny lines in the docs:
    WriteBrightnessLevel X - sets brightness to X% (0-100)*
    ReadBrightnessLevel X - sets brightness to X% (0-100)*

    However, below works to get monitor brightness (pip install monitorcontrol)
    throws an error if you open the monitor settings menu on U2415..
    '''
    import monitorcontrol
    m = monitorcontrol.get_monitors()[0]
    with m:
        while 1:
            try:
                lum = m.get_luminance()
                break
            except:
                print('Menu open?!')
                time.sleep(1)
        return lum

def brightness_from_LDR():
    # Fancy way that reads room brightness from arduino
    # Just a voltage divider with an LDR.
    # 100 mV in the sun
    # ~2 V daytime normal light
    # 3.3 V in the dark
    import serial

    #s = serial.Serial('COM6')

    # This won't open the port yet
    s = serial.Serial()
    #s.setPort('COM6')
    s.setPort('COM7')
    s.timeout = 5

    # code shouldn't stop if you update firmware or reset the microcontroller
    vsamples = None
    try:
        s.open()
        if False:
            # Free running version -- needs appropriate firmware
            time.sleep(.5)  # Wait for some samples
            vsamples = [float(v) for v in s.read_all().decode().split('\r\n') if v]
        else:
            # Query version
            s.write('500\n'.encode()) # Ask for ~500 ms of brightness data
            vsamples = [float(s.readline().strip())]
        s.close()
    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        #print('Problem with COM connection!')
        print(e)
        s.close()

    if vsamples:
        vmean = sum(vsamples) / len(vsamples)
        vmin = .2 # at this voltage and below, we'll be at maxbrightness
        vmax = 3.295
        vnorm = 1 - (vmean - vmin) / (vmax - vmin)
        vnorm = min(1, max(0, vnorm)) # clip
        # Maybe a power law works?
        exponent = .35
        brightness = minbrightness + vnorm**exponent * (maxbrightness - minbrightness)
        return brightness # yes as a float
    else:
        return None

def brightness_from_suntime():
    try:
        from suntime import Sun
    except:
        return None
    sun = Sun(50.7753, 6.0839)
    rise = sun.get_local_sunrise_time()
    set = sun.get_local_sunset_time()
    dayfrac = (now - rise) / (set - rise)
    dayfrac = max(dayfrac, 0)
    dayfrac = min(dayfrac, 1)
    # always at minbrightness while sun is set
    brightness = int(round(minbrightness + (maxbrightness - minbrightness) * sin(dayfrac*pi)))
    return brightness

def brightness_the_dumb_way():
    # Simply a sine function.
    nowDec = now.hour + now.minute/60
    maxtime = 12
    brightness = int(round(minbrightness + (maxbrightness - minbrightness) * (1 + cos((nowDec - maxtime)*2*pi/24))/2))

def set_brightness_continuously():
    lastbrightness = get_brightness()
    while True:
        brightness = brightness_from_LDR()
        if brightness:
            bright_diff = brightness - lastbrightness

            lum = get_luminance()
            if lum != lastbrightness:
                print('Brightness manually adjusted, disengaging...')
                while True:
                    time.sleep(5)
                    brightness = brightness_from_LDR()
                    if abs(brightness - lastbrightness) <= .5:
                        print('Manual brightness agrees with automatic value again, resuming control')
                        bright_diff = 0
                        break

            # A bit of hysteresis so we don't send constant updates due to noise if the brightness is near a transition
            if abs(bright_diff) > 0.8:
                lastbrightness = set_brightness(brightness, log=False)
        else:
            time.sleep(3)

if __name__ == '__main__':
    # Try different ways to calculate brightness, fall back to simpler ways.
    brightness = brightness_from_LDR()
    if brightness:
        way = 'LDR'
    else:
        brightness = brightness_from_suntime()
        if brightness:
            way = 'suntime'
        else:
            brightness = brightness_the_dumb_way()
            way = 'sin'

    if bypass:
        print('Bypass on')
    else:
        set_brightness(brightness)