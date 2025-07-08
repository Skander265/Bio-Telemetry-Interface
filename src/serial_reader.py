
import serial
import time

def connect_serial(port='COM3', baudrate=115200, timeout=1):
    ser = serial.Serial(port, baudrate, timeout=timeout)
    time.sleep(2)  
    return ser

def read_line(ser):
    try:
        line = ser.readline().decode('utf-8').strip()
        if ',' in line:
            timestamp_str, voltage_str = line.split(',')
            return int(timestamp_str), float(voltage_str)
    except Exception as e:
        print(f"Error reading line: {e}")
    return None, None
