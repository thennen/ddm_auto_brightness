import os
import time

# This also works!
# (pip install monitorcontrol)
# but throws an error if you open the monitor settings menu
import monitorcontrol
m = monitorcontrol.get_monitors()[0]
#with m: m.set_luminance(50)
#with m: l = m.get_luminance()

maxbrightness = 100
minbrightness = 5

import serial

# This won't open the port yet
s = serial.Serial()
#s.setPort('COM6')
s.setPort('COM7')
s.timeout = 5

#lastbrightness = brightness =  40
def get_luminance():
    with m:
        while 1:
            try:
                lum = m.get_luminance()
                break
            except:
                print('Menu open?!')
                time.sleep(1)
        return lum

lastbrightness = brightness = get_luminance()

while True:
    # Fancy way that reads room brightness from arduino
    # Just a voltage divider
    # 100 mV in the sun
    # ~2 V daytime normal light
    # 3.3 V in the dark
    # Wait for some samples

    # code shouldn't stop if you update firmware or reset the microcontroller
    try:
        s.open()
        if False:
            # Free running version
            time.sleep(.5)
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
        time.sleep(3)
        continue

    if vsamples:
        vmean = sum(vsamples) / len(vsamples)
        vmin = .2 # at this voltage and below, we'll be at maxbrightness
        vmax = 3.295
        vnorm = 1 - (vmean - vmin) / (vmax - vmin)
        vnorm = min(1, max(0, vnorm)) # clip
        # Maybe a power law works?
        exponent = .35
        brightness = minbrightness + vnorm**exponent * (maxbrightness - minbrightness)
        bright_diff = brightness - lastbrightness
        bright_int = int(round(brightness))

    
    lum = get_luminance()
    if lum != lastbrightness:
        # brightness was manually changed -- take a break
        print('Brightness manually adjusted, taking a break...')
            else:
                print('Manual brightness close enough to automatic value, resuming')
                break

    # A bit of hysteresis so we don't send constant updates due to noise if the brightness is near a transition
    if abs(bright_diff) > 0.8:
        os.system(fr'"C:\Program Files (x86)\Dell\Dell Display Manager\ddm.exe" /SetBrightnessLevel {bright_int}')
        print(bright_int)
        lastbrightness = bright_int