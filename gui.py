from tkinter import *
import time
import threading
from Dart import Dart
import ScoreEvaluator

window = Tk()
window.config(bg='white')
window.geometry('480x290')
window.attributes('-fullscreen', True)

button = Button(window)

def start_game():
    button.pack_forget()
    t = threading.Thread(target=game)
    t.start()

def game():
    '''
    Runs a game of dart. Three throws per player, displays score for each throw.
    '''
    dart = Dart()
    score = Label(window, font=('Courier',44), bg='white')
    score.config(anchor=CENTER)
    score.config(text='Welcome to dart!', bg='white')
    score.pack(fill=BOTH, expand=1)

    time.sleep(5)
    for i in range(2):
        score.config(text=f'Player {i+1}')
        time.sleep(3)
        val = 0

        for i in range(3):
            window.config(bg='green')
            score.config(text='Score: ')
            val += dart.start_round()
            score.config(text=f'Score: {val}')
            window.config(bg='white')
            time.sleep(5)
    
    score.pack_forget()
    button.grid(column=1, row=1, sticky=N+S+E+W)
    window.grid_columnconfigure(1,weight=50)

    button.pack(fill=BOTH, expand=1)

button.config(text='Press Me!', font=('Courier',44), bg='white', command=start_game)
button.grid(column=1, row=1, sticky=N+S+E+W)
window.grid_columnconfigure(1,weight=50)

button.pack(fill=BOTH, expand=1)

window.mainloop()
