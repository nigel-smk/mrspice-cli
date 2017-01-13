from repository.repository import Repository
import requests
import json

class YummlyIngredientsService:

    URL = "http://api.yummly.com/v1/api/metadata/ingredient"
    APP_ID = "2a6406ac"
    APP_KEY = "c0aac363d1a1c8b1925e5f8898c69a48"

    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.database = kwargs.get('database')

        self.db = Repository(self.host, self.database)
        self.collection = self.db.get_collection(kwargs.get('collection'))

        self.skip = kwargs.get("skip")

    def get_ingredients(self):

        headers = {
            'X-Yummly-App-ID': YummlyIngredientsService.APP_ID,
            'X-Yummly-App-Key': YummlyIngredientsService.APP_KEY
        }

        r = requests.get(YummlyIngredientsService.URL, headers=headers)
        response_body = r.text
        # trim jsonp  callback
        response_body = response_body.partition(',')[2][:-2]
        response_json = json.loads(response_body)

        self.collection.insert_many(response_json)