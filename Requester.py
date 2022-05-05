import requests

IP = 'http://78.70.59.155:2256/'

class Requester:
    '''
    Requester class that implements score posting and deleting
    '''

    @staticmethod
    def post_scores(p1, p2):
        '''
        Post scores to the specified address

        p1
            Player 1 score
        p2
            Player 2 score
        '''
        requests.post(IP, json={"p1_score":p1,"p2_score":p2})

    @staticmethod
    def delete_scores():
        '''
        Deletes scores to the specified address
        '''
        requests.delete(IP)
