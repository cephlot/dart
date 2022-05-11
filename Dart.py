from ImageAnalyzer import ImageAnalyzer
from ScoreEvaluator import ScoreEvaluator
from GameMode import GameMode301
from GUI import Game_GUI

from Requester import Requester
import MotionDetector
import threading
import time

class Dart:
    '''
    Class that represents a game of Dart
    '''

    def __init__(self):
        self.detector       = MotionDetector.MotionDetector()

        self.game_mode      = GameMode301()
        self.GUI            = Game_GUI()

    def start(self):
        self.GUI.show_start_screen(self.choose_player_amount)
    
    def choose_player_amount(self):
        self.GUI.choose_player_amount(lambda x: self.create_game(x))

    def create_game(self, player_count):

        #number_of_players = self.GUI.choose_player_amount()
        #self.game_mode.start_game(number_of_players)

        print("Player_count", player_count)
        self.game_mode.start_game(player_count)

        t = threading.Thread(target=self.game)
        t.start()
        self.GUI.show_game_screen()

    def wait(self):
        frames_before, frames_after = self.detector.wait_for_motion()
        self.frames_before = frames_before
        self.frames_after = frames_after

    def get_score(self):
        '''
        Gets the score from a dart by using evaluator
        '''
        print("BEFORE")
        print(len(self.frames_before))
        evaluator = ScoreEvaluator(self.frames_before)
        return evaluator.evaluate(self.frames_before, self.frames_after)

    def wait_detect(self):
        '''
        Waits for motion to be detected and then determines if there's a change 
        of players.
        '''

        condition = False

        while condition is False:
            frames_before, frames_after = self.detector.wait_for_motion()

            # analyse image
            condition = ImageAnalyzer.analyze(self.frames_before, frames_after)

        # Set new background
        self.frames_before = frames_after


    def game(self):
        self.GUI.show_game_screen()
        self.detector.open_cameras()
        self.GUI.show_waiting_screen()

        time.sleep(3)
        self.wait()

        score = self.get_score()

        self.GUI.show_score(score)


dart = Dart()
dart.start()




