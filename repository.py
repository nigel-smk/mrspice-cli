from pymongo import MongoClient


class Repository:

    def __init__(self, url, database):
        self.client = MongoClient(url) if url else MongoClient()
        self.db = self.client[database]

    def get_collection(self, collection):
        return self.db[collection]

    def set_database(self, database):
        self.db = self.client[database]
