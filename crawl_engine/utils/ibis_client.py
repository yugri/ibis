import requests
from django.conf import settings


class IbisClient(object):
    def __init__(self, ibis_address=None):
        self.ibis_url = ibis_address or settings.IBIS_ADDRESS

    def post(self, url, data):
        return requests.post(
            self.ibis_url + url,
            json=data
        )

    def push_articles(self, data):
        response = self.post(
            url='articles/',
            data=data
        )
        return response
