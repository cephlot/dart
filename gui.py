from tkinter import *
import time
import threading
from Dart import Dart
import ScoreEvaluator

window = Tk()
window.config(bg='white')
window.geometry('480x290')
window.attributes('-fullscreen', True)

frame = Frame()

score = Label(frame, text='Score: ', font=('Courier', 44), bg='white')
score.config(anchor=CENTER)

frame.pack(expand=True)
score.pack()

def eval():
    # Put dart logic here!
    while True:
        dart = Dart()
        window.config(bg='green')
        score.config(text=f'Score: {dart.start_round()}')
        time.sleep(5)
        window.config(bg='white')
        score.config(text='Score: ')
        dart.__del__()

x = threading.Thread(target=eval)
x.start()

window.mainloop()
