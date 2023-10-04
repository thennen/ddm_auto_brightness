import serial
from matplotlib import pyplot as plt

s = serial.Serial('COM6')

fig, ax = plt.subplots()
x = 0
line = ax.plot([x],[np.nan])
ax.set_ylim(0, 3.3)
ax.set_xticks([])
s.reset_input_buffer()

while plt.fignum_exists(fig.number):
    linedata = line[0].get_data()
    x = linedata[0][-1] + 1
    # code shouldn't stop if you update firmware or reset the microcontroller
    try:
        t = s.readline().decode().strip()
    except:
        plt.pause(3)
        s = serial.Serial('COM6')
        t = s.readline().decode().strip()
    try:
        y = float(t)
    except:
        continue
    line[0].set_data(np.append(linedata[0], x),
                     np.append(linedata[1], y))
    ax.set_xlim(x-1000, x)
    plt.pause(.001) # If update is slower than microcontroller messages we will fall behind ..

s.close()