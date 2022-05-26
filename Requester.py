import requests

IP = 'http://78.70.59.155:2256/'

class Requester:
    """
    Requester class that implements score posting and deleting
    """

    @staticmethod
    def post_scores_without_latest(scores, current_player):
        """Post scores to the specified address

        :param scores: list of player scores
        :type scores: int list
        :param current_player: current player index
        :type current_player: int
        """
        assert isinstance(current_player, int)
        requests.post(IP, json={"player_scores": scores, "current_player": current_player})

    @staticmethod
    def post_scores(scores, score, current_player):
        """Post scores to the specified address

        :param scores: list of player scores
        :type scores: int list
        :param current_player: current player index
        :type current_player: int
        :param score: latest score
        :type score: int
        """
        assert isinstance(current_player, int)
        requests.post(IP, json={"player_scores": scores, "current_player": current_player, "latest_score": score})
    
    @staticmethod
    def post_coords(x, y):
        """Post dart coordinates to scoreboard

        :param x: x value of dart
        :type x: int
        :param y: y value of dart
        :type y: int
        """        
        requests.post(IP+"coord", json={"x": x, "y": y})

    @staticmethod
    def delete_scores():
        """Deletes scores to the specifed address
        """
        
        requests.delete(IP)
    
    @staticmethod
    def delete_coords():
        """Deletes dart coordinates on scoreboard
        """        
        requests.delete(IP+"coord")
