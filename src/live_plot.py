import matplotlib.pyplot as plt
from collections import deque

def setup_plot(window_size=500):
    plt.ion()
    fig, ax = plt.subplots()
    ax.set_title("Real-Time Bioelectric Signal")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Voltage (mV)")
    line, = ax.plot([], [], lw=2)
    ax.set_xlim(0, window_size)
    ax.set_ylim(0, 5000)
    return fig, ax, line, deque(maxlen=window_size), deque(maxlen=window_size)

def update_plot(fig, ax, line, x_data, y_data, new_x, new_y):
    x_data.append(new_x)
    y_data.append(new_y)
    line.set_data(x_data, y_data)
    ax.set_xlim(max(0, new_x - 500), new_x)
    ax.figure.canvas.draw()
    ax.figure.canvas.flush_events()
