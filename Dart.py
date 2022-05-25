from ImageAnalyzer import ImageAnalyzer
from ScoreEvaluator import ScoreEvaluator
from GameMode import GameMode301, GameStatus
from GUI import Game_GUI
import cv2 as cv

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
        self.evaluator      = None

        self.game_mode      = GameMode301()
        self.GUI            = Game_GUI()
        self.frames_before  = None
        self.frames_before_before  = None
        self.frames_after   = None

    def start(self):
        self.GUI.show_start_screen(self.choose_player_amount)
    
    def choose_player_amount(self):
        self.GUI.choose_player_amount(lambda x: self.create_game(x))

    def create_game(self, player_count):
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
        #frames_before, frames_after = Dart.resize_images(frames_before, frames_after)
        self.frames_before = frames_before
        self.frames_after = frames_after

        if(first_dart):
            self.frames_before_before = frames_before

    def get_score(self):
        """Gets the score from a dart by using evaluator.


        :return: a score evaluation
        :rtype: int
        """
        return self.evaluator.evaluate(self.frames_before, self.frames_after)

    def wait_detect(self):
        """Waits for motion to be detected and then determines if there's a change 
        of players.
        """        

        condition = False

        while condition is False:
            frames_before, frames_after = self.detector.wait_for_motion()
            
            condition = ImageAnalyzer.analyze(self.frames_before_before, frames_after)

        self.frames_before = frames_after


    def create_new_matrix(self):
        """wrapper for create_projection_matrix, will generate a new ScoreEvaluator if needed
        """        
        if(self.evaluator == None):
            self.evaluator = ScoreEvaluator()
        self.evaluator.create_projection_matrix(self.frames_before)

    def initialize_GUI(self):
        self.GUI.show_game_screen()
        self.detector.open_cameras()
        self.GUI.show_waiting_screen()


    def game(self):
        self.initialize_GUI()
        first_dart = True

        while(self.game_mode.get_game_status() == GameStatus.ONGOING):
            self.wait(first_dart)

            if(first_dart):
                self.create_new_matrix()
                first_dart = False

            score, coords = int(self.get_score())
            self.GUI.show_score(score)
            self.game_mode.give_points(score, coords) 

            if self.game_mode.get_game_status() == GameStatus.GET_DARTS:
                time.sleep(2)
                self.GUI.show_get_darts_screen(score)
                self.wait_detect()
                self.game_mode.set_game_status(GameStatus.ONGOING)
                first_dart = True
                self.GUI.show_waiting_screen()
            else:
                self.GUI.show_waiting_screen(show_score=True, Score=score)

        print("Game over!")


    def resize_images(frames_before, frames_after):
        
        for i,_ in enumerate(frames_before):
            frames_before[i] = cv.resize(frames_before[i], (1280,720))
            frames_after[i] = cv.resize(frames_after[i], (1280,720))
        return frames_before, frames_after

if __name__ == '__main__':
    dart = Dart()
    dart.start()




