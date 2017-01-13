from common import output

from common.progress_bar import ProgressBar
from repository.repository import Repository
from repository.neo4j_model import Recipe, Ingredient, reset_graph


class PopulateGraphService:

    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.neoHost = kwargs.get('neoHost')
        self.database = kwargs.get('database')
        self.resume = kwargs.get('resume')

        self.db = Repository(self.host, self.database)
        self.recipes = self.db.get_collection(kwargs.get('recipes'))

    def populate(self):
        #TODO set uniqueness constraints if not exists
        reset_graph()

        records_count = self.recipes.count()
        output.push('Populating graph...')
        progress = ProgressBar(records_count)
        processed = 0
        progress.start()

        cursor = self.recipes.find()
        for record in cursor:

            web_id = record['id']
            recipeName = record['recipeName']
            recipe = Recipe(id=web_id)

            ingredients = []
            for ingredient_result in record['ingredients']:
                ingredients.append(Ingredient(name=ingredient_result))

            recipe.add()
            recipe.require_ingredients(ingredients)

            processed += 1
            if processed % 100 == 0:
                progress.update(processed)

        progress.update(processed)
        cursor.close()
        progress.end()
