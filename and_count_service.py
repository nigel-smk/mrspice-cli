from repository import Repository
from count_progress_bar import CountProgress
import itertools


class AndCountService:

    def __init__(self, **kwargs):
        self.db = Repository(kwargs.get('host'), kwargs.get('database'))
        self.source = self.db.get_collection(kwargs.get('source'))
        self.destination = self.db.get_collection(kwargs.get('destination'))
        self.skip = kwargs.get('skip')
        self.r_min = kwargs.get('r_min')
        self.r_max = kwargs.get('r_max')

    def count_and(self):

        """exceptions:
            not a recipe data store
            source does not exist
            destination already exists
            r_max/r_min is not an integer
        """

        # TODO register exit handler to print recipes processed on unexpected exit
        # TODO https://docs.python.org/3/library/atexit.html

        recipe_count = self.source.count()
        cursor = self.source.find(no_cursor_timeout=True)
        # TODO timeout=False is bad practice
        if self.skip:
            cursor.skip(self.skip)
            processed = self.skip
        else:
            processed = 0

        progress = CountProgress(recipe_count)
        progress.start()

        for recipe in cursor:
            ingredients = recipe['ingredients']
            ingredients.sort()

            # for each possible length of combinations between r_min and r_max
            r_min = int(self.r_min)
            r_max = self.r_max
            r_max = int(r_max) if r_max and len(ingredients) > int(r_max) else len(ingredients)
            for r in range(r_min, r_max + 1):
                combinations = itertools.combinations(ingredients, r)
                # for each combination of that length
                for c in combinations:
                    # ensure that ingredients in id are alphabetically ordered
                    c = list(c)
                    c.sort()
                    combo_id = '::'.join(c)
                    self.destination.update_one(
                        {"_id": combo_id},
                        {
                            "$set": {
                                "_id": combo_id,
                                "r": r,
                                "ingredients": c
                            },
                            "$inc": {
                                "and_count": 1
                            }
                        },
                        upsert=True
                    )
            processed += 1
            progress.update(processed)

        cursor.close()
        progress.end()
