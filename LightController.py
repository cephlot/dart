import time
from serial import Serial

class LightController:
    def __init__(self):
        self.ser = Serial(port='COM5', baudrate=115200)
        time.sleep(2)
        self.clear()

    def __del__(self):
        self.clear()
        self.ser.close()

    def red(self):
        self.ser.write(b'r')

    def green(self):
        self.ser.write(b'g')

    def blue(self):
        self.ser.write(b'b')

    def white(self):
        self.ser.write(b'w')

    def clear(self):
        self.ser.write(b'c')

    def rainbow(self):
        self.ser.write(b'R')

    def flash(self):
        self.ser.write(b'f')

    def loading(self):
        self.ser.write(b'l')
