from repository import Repository


class IndexService:

    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.database = kwargs.get('database')

        self.db = Repository(self.host, self.database)
        self.recipes = self.db.get_collection(kwargs.get('recipes'))
        self.combinations = self.db.get_collection(kwargs.get('combinations'))

    def index(self):

        self.recipes.create_index('ingredients')
        self.combinations.create_index('r')
