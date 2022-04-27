from tkinter import *
import time
import threading
from Dart import Dart
import ScoreEvaluator

window = Tk()
window.geometry('480x290')
window.attributes('-fullscreen', True)

frame = Frame()

score = Label(frame, text='Score: ', font=('Courier', 44))
score.config(anchor=CENTER)

frame.pack(expand=True)
score.pack()

def eval():
    # Put dart logic here!
    dart = Dart()
    score.config(text=f'Score: {dart.start_round()}')

x = threading.Thread(target=eval)
x.start()

window.mainloop()
