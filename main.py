# Firmware for a very simple light sensor (CircuitPython, Feather M4 Express)
# prints out a voltage reading (0 - 3.3) very frequently

import board
import neopixel
from analogio import AnalogIn

LDRpin = AnalogIn(board.A2)

# neopixel produces light which might interfere with measurement
# turn it off
pixel_pin = board.NEOPIXEL
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0, auto_write=False)

while True:
    # oversampling
    nsamples = 1000
    val = 0
    for _ in range(nsamples):
        val += LDRpin.value
    val /= nsamples
    print(val / 2**16 * 3.3)