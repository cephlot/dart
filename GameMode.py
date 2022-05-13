from Requester import Requester
from enum import Enum
import abc

class GameStatus(Enum):
	ONGOING 	= 0
	GET_DARTS 	= 1
	GAME_OVER 	= 2
	GAME_WON  	= 3

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

	def start_game(self, player_count):
		super().start_game(player_count)
		self.scores = [301] * self.player_count

		self.game_status 	= GameStatus.ONGOING
		self.current_player = 0
		self.throw_count 	= 0
		self.prev_score 	= 0

		Requester.post_scores(self.scores)

	def give_points(self, score):

		if (self.game_status != GameStatus.ONGOING):
			return

		assert isinstance(score, int)
		self.scores[self.current_player] -= score

		if (self.scores[self.current_player] == 0):
			self.game_status = GameStatus.GAME_WON
			self.winner = self.current_player
			return
		elif (self.scores[self.current_player] < 0):
			self.change_player()

		self.throw_count += 1
		if (self.throw_count >= 3):
			print("lmao xd")
			self.change_player()
			self.game_status = GameStatus.GET_DARTS

		Requester.post_scores(self.scores)

	def change_player(self):
		self.current_player = (self.current_player + 1) % self.player_count
		self.prev_score = self.scores[self.current_player]
		self.throw_count = 0


