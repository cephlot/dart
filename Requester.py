import requests

IP = 'http://78.70.59.155:2256/'

class Requester:
    @staticmethod
    def post_scores(p1, p2):
        requests.post(IP, json={"p1_score":p1,"p2_score":p2})

    @staticmethod
    def delete_scores():
        requests.delete(IP)
