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
frame.pack(expand=True)

def eval():
    # Put dart logic here!
    score = Label(frame, text='Welcome to dart!', font=('Courier', 44), bg='white')
    score.pack()
    score.config(anchor=CENTER)

    dart = Dart()
    while True:
        for i in range(2):
            score.config(text=f'Player {i+1}')
            time.sleep(3)
            val = 0;

            for i in range(3):
                window.config(bg='green')
                score.config(text='Score: ')
                val += dart.start_round()
                score.config(text=f'Score: {val}')
                window.config(bg='white')
                time.sleep(5)

x = threading.Thread(target=eval)
x.start()

window.mainloop()
