from tkinter import *
import time
import copy

class Game_GUI(object):
    """docstring for GUI"""
    def __init__(self):
        self.window = Tk()
        self.window.config(bg='white')
        self.window.geometry('480x290')
        self.window.attributes('-fullscreen', True)


        self.top = Frame(self.window)
        self.bottom = Frame(self.window,)        
        self.button = Button(self.window)
        self.start_game_button = Button(self.window)
        self.exit_button = Button(self.window)
        self.title = Label(self.window, font=('Elephant Pro',72), bg='white')
        self.score = Label(self.window, font=('Courier',44), bg='white')

        self.player_ids = range(2, 5)
        self.max_player_count = len(self.player_ids)

    def show_game_screen(self):
        for i in range(self.max_player_count):
            self.player_amount_button[i].pack_forget()

        self.score.config(anchor=CENTER) #Show game screen
        self.score.config(text='Welcome to dart!', bg='white')
        self.score.pack(fill=BOTH, expand=1)

    def change_on_hover(self, button, color_enter, color_leave):        
        button.bind("<Enter>", func=lambda event: button.config(
        background=color_enter))

        button.bind("<Leave>", func=lambda event: button.config(
        background=color_leave))        


    def show_start_screen(self, start_command):
        self.title.config(anchor=CENTER)
        self.title.config(text='D.A.R.T', bg='black', foreground='white')
        self.title.pack(side=TOP, fill=BOTH, expand=1)
        
        self.start_game_button.config(text='Start', font=('Courier',44), bg='#0d7a1a', foreground='black', height=5, command=start_command)
        self.start_game_button.pack(side=LEFT, fill=BOTH, expand=1)

        self.exit_button.config(text='Exit', font=('Courier',44), bg='#ba1411', foreground='black', height=5, command=self.exit_game)
        self.exit_button.pack(side=LEFT, fill=BOTH, expand=1)  

        self.change_on_hover(self.start_game_button, '#13ad25', '#0d7a1a')
        self.change_on_hover(self.exit_button, '#e82723', '#ba1411')

        self.window.mainloop()


    def choose_player_amount(self, command):
        self.start_game_button.pack_forget() #Hide start screen
        self.exit_button.pack_forget()
        self.title.pack_forget()

        self.player_amount_button = [None] * self.max_player_count
        for i in range(self.max_player_count):
            p_id = self.player_ids[i]

            self.player_amount_button[i] = Button(self.window)
            self.player_amount_button[i].config(text=str(p_id), font=('Courier',72), bg='#ba1411', foreground='black', command=lambda k=p_id : command(k))
            self.change_on_hover(self.player_amount_button[i], '#e82723', '#ba1411')
            self.player_amount_button[i].pack(side=LEFT, fill=BOTH, expand=1)

    def show_score(self, score):
        assert isinstance(score, int)
        self.score.config(text=f'Score: {score}')
        self.score.config(bg='white')

    def show_waiting_screen(self, show_score=False, Score=0):
        if show_score:
            self.score.config(text=f'Waiting for dart\nscore: {Score}')
        else:
            self.score.config(text='Waiting for dart')
        self.score.config(bg='white')

    def show_get_darts_screen(self, score):
        self.score.config(text=f'Get your darts!\nscore: {score}')
        self.score.config(bg='white')

    def exit_game(self):
        self.window.quit()

    def simple_dart_game(self):
        '''
        Simulates three throws per player (2 players).
        Displays the score after each throw.
        Uses Dart.py to simulate the game.
        '''
        #dart = Dart()

        for i in range(2):
            self.score.config(text=f'Player {i+1}')
            time.sleep(1)
            val = 0

            for i in range(3):
                self.score.config(bg='green') #setScore()
                self.score.config(text='Score: ') #setScore()
                #dart.wait()
                #val += dart.get_score()
                self.score.config(text=f'Score: {val}') #setScore()
                self.window.config(bg='white')
                time.sleep(1)
                
            self.score.config(text=f'Get your darts!')
            #dart.wait_detect()


        self.score.pack_forget()
        #self.button.grid(column=1, row=1, sticky=N+S+E+W)
        #self.button.pack(fill=BOTH, expand=1)
