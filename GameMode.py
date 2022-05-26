from LightController import LightController
from urllib.request import Request
from Requester import Requester
from enum import Enum
import threading
import time
import abc

SERIAL_PORT = '/dev/ttyUSB0'

class GameStatus(Enum):
	ONGOING 	= 0
	GET_DARTS 	= 1
	GAME_OVER 	= 2
	GAME_WON  	= 3
	WAIT  		= 4

class GameMode(object):
	"""Pogger"""
	def __init__(self):
		self.player_count 	= None
		self.scores 		= None
		self.current_player = None
		self.game_status 	= None
		self.winner 		= None 
	
	@abc.abstractmethod
	def start_game(self, player_count):
		assert isinstance(player_count, int)
		self.player_count = player_count

	@abc.abstractmethod
	def give_points(self, score):
		pass

	def get_game_status(self):
		return self.game_status

	def set_game_status(self, game_status):
		self.game_status = game_status

	def get_player_scores(self):
		return self.scores


class GameMode301(GameMode):
	"""Pogger"""
	def __init__(self):
		super().__init__()
		self.throw_count 	= None
		self.prev_score 	= None
		self.light = LightController(SERIAL_PORT)

	def start_game(self, player_count):
		super().start_game(player_count)
		self.scores = [301] * self.player_count

		self.game_status 	= GameStatus.ONGOING
		self.current_player = 0
		self.throw_count 	= 0
		self.prev_score 	= 0

		self.light.white()
		Requester.post_scores(self.scores, self.current_player)
		Requester.delete_coords()

	def feedback(self):
		self.light.green()
		time.sleep(0.25)
		self.light.white()
		time.sleep(0.25)
		self.light.green()
		time.sleep(0.25)
		self.light.white()
		time.sleep(0.25)
		time.sleep(0.5)

	def feedback_high(self):
		self.light.rainbow()
		time.sleep(1)
		self.light.white()
		time.sleep(0.5)
		

	def give_points(self, score, coords):

		if (self.game_status != GameStatus.ONGOING):
			return

		assert isinstance(score, int)
		self.scores[self.current_player] -= score

		if (self.scores[self.current_player] == 0):
			self.game_status = GameStatus.GAME_WON
			self.winner = self.current_player
			return
		elif (self.scores[self.current_player] < 0):
			self.scores[self.current_player] = self.prev_score
			self.change_player()

		self.feedback()

		self.throw_count += 1
		if (self.throw_count >= 3):
			self.change_player()

		Requester.post_scores(self.scores, self.current_player)
		Requester.post_coords(coords[0], coords[1])

	def change_player(self):
		self.game_status = GameStatus.GET_DARTS
		self.current_player = (self.current_player + 1) % self.player_count
		self.prev_score = self.scores[self.current_player]
		self.throw_count = 0


