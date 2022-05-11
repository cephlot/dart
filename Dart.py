from ImageAnalyzer import ImageAnalyzer
from ScoreEvaluator import ScoreEvaluator
from GameMode import GameMode301, GameStatus
from GUI import Game_GUI

from Requester import Requester
import MotionDetector
import threading
import time

class Dart:
    """
    Class that represents a game of Dart
    """

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

    def wait(self, first_dart):
        """Wrapper for MotionDetector.wait_for_motion. Stores frames before and 
        frames after.
        """

        frames_before, frames_after = self.detector.wait_for_motion()
        self.frames_before = frames_before
        self.frames_after = frames_after

        if(first_dart):
            self.frames_before_before = frames_before

    def get_score(self):
        """Gets the score from a dart by using evaluator.


        :return: a score evaluation
        :rtype: int
        """        
        print("BEFORE")
        print(len(self.frames_before))
        evaluator = ScoreEvaluator(self.frames_before)
        return evaluator.evaluate(self.frames_before, self.frames_after)

    def wait_detect(self):
        """Waits for motion to be detected and then determines if there's a change 
        of players.
        """        

        condition = False

        while condition is False:
            frames_before, frames_after = self.detector.wait_for_motion()
            
            condition = ImageAnalyzer.analyze(self.frames_before_before, frames_after)

        self.frames_before = frames_after


    def game(self):
        self.GUI.show_game_screen()
        self.detector.open_cameras()
        self.GUI.show_waiting_screen()

        time.sleep(1)

        self.wait(True)
        score = int(self.get_score())
        self.GUI.show_score(score)
        self.game_mode.give_points(score)
        time.sleep(2)
        self.GUI.show_waiting_screen()

        while(self.game_mode.get_game_status() == GameStatus.ONGOING):
            self.wait(False)
            score = int(self.get_score())
            self.GUI.show_score(score)
            self.game_mode.give_points(score)
            time.sleep(2)

            if self.game_mode.get_game_status() == GameStatus.GET_DARTS:
                self.GUI.show_get_darts_screen()
                self.wait_detect()
                self.game_mode.set_game_status(GameStatus.ONGOING)

            self.GUI.show_waiting_screen()

        print("Game over!")


dart = Dart()
dart.start()




