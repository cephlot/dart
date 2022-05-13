import requests

IP = 'http://78.70.59.155:2256/'

class Requester:
    """
    Requester class that implements score posting and deleting
    """

    @staticmethod
    def post_scores(scores):
        """Post scores to the specified address

        :param scores: list of player scores
        :type scores: int list
        """
        
        requests.post(IP, json={"player_scores": scores})

    @staticmethod
    def delete_scores():
        """Deletes scores to the specifed address
        """
        
        requests.delete(IP)
