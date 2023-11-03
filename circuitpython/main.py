# Firmware for a very simple light sensor (CircuitPython, Feather M4 Express)
# prints out a voltage reading (0 - 3.3) very frequently

import board
import neopixel
import usb_cdc
from analogio import AnalogIn

# Problem with usb_cdc, breaks USB if you don't wait here
# Also breaks USB if you do wait here ...
import supervisor
while not supervisor.runtime.usb_connected:
    pass

LDRpin = AnalogIn(board.A2)

# neopixel produces light which might interfere with measurement
# turn it off
pixel_pin = board.NEOPIXEL
pixels = neopixel.NeoPixel(pixel_pin, 1, brightness=0, auto_write=False)

while True:
    if True:
        # Only send data when requested
        #nsamples = input()
        nsamples = usb_cdc.data.readline().strip()
        try:
            # We get roughly 16 ksamples per second
            # now the input is roughly number of milliseconds to measure
            nsamples = int(nsamples) * 16
        except:
            nsamples = 1
    else:
        nsamples = 1000
    val = 0
    for _ in range(nsamples):
        val += LDRpin.value
    val /= nsamples
    #print(val / 2**16 * 3.3)
    usb_cdc.data.write(f'{val / 2**16 * 3}\n'.encode())