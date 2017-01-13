from repository.repository import Repository
import requests


class USDAService:

    URL = "http://api.nal.usda.gov/ndb"
    API_KEY = "6KzqP5T5nx7Y19K7pHzowtPMwuJitqghgZleBfwe"

    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.database = kwargs.get('database')

        self.db = Repository(self.host, self.database)
        self.collection = self.db.get_collection(kwargs.get('collection'))

        self.skip = kwargs.get("skip")

    def get_foods(self):
        max = 1500
        offset = 0

        while True:
            params = {
                'ds': 'Standard Reference',
                'max': max,
                'offset': offset,
                'api_key': USDAService.API_KEY
            }

            headers = {
                'Content-Type': 'application/json'
            }

            r = requests.get(USDAService.URL + '/search', params=params, headers=headers)
            records = r.json()
            self.collection.insert_many(records['list']['item'])
            print("Got some.")

            offset += max

            if records['list']['total'] <= offset:
                break
