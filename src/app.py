from serial_reader import connect_serial, read_line
from noise_filter import MovingAverageFilter
from live_plot import setup_plot, update_plot

def main():
    port = 'COM3'  
    ser = connect_serial(port)
    filter = MovingAverageFilter(window_size=5)
    
    fig, ax, line, x_data, y_data = setup_plot()

    try:
        while True:
            timestamp, voltage = read_line(ser)
            if timestamp is not None:
                filtered = filter.apply(voltage)
                update_plot(fig, ax, line, x_data, y_data, timestamp, filtered)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        ser.close()

if __name__ == '__main__':
    main()
