import requests

IP = 'http://78.70.59.155:2256/'

class Requester:
    """
    Requester class that implements score posting and deleting
    """

    @staticmethod
    def post_scores(p1, p2):
        """Post scores to the specified address

        :param p1: player 1 score
        :type p1: int
        :param p2: player 2 score
        :type p2: int
        """
        
        requests.post(IP, json={"p1_score":p1,"p2_score":p2})

    @staticmethod
    def delete_scores():
        """Deletes scores to the specifed address
        """
        
        requests.delete(IP)
