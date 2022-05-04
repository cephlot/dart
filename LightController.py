import time
from serial import Serial

class LightController:
    def __init__(self):
        self.ser = Serial(port='COM5', baudrate=115200)
        time.sleep(2)
        self.pixels_clear()

    def __del__(self):
        self.pixels_clear()
        self.ser.close()

    def pixels_red(self):
        self.ser.write(b'r')

    def pixels_green(self):
        self.ser.write(b'g')

    def pixels_blue(self):
        self.ser.write(b'b')

    def pixels_white(self):
        self.ser.write(b'w')

    def pixels_clear(self):
        self.ser.write(b'c')

light_controller = LightController()

while True:
    light_controller.pixels_red()
    time.sleep(1)
    light_controller.pixels_green()
    time.sleep(1)
    light_controller.pixels_blue()
    time.sleep(1)