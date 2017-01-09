import output
from repository import Repository
from progress_bar import ProgressBar
import itertools
import functools


class OrCountService:

    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.database = kwargs.get('database')

        self.db = Repository(self.host, self.database)
        self.combinations = self.db.get_collection(kwargs.get('combinations'))

        self.r_min = int(kwargs["r_min"])
        self.r_max = int(kwargs["r_max"])
        self.skip = kwargs.get("skip")

    def count_or(self):

        """exceptions:
            not a collections data store
            collection does not exist
            r_max/r_min is not an integer
            r_min/r_max are currently required (should be optional)
        """

        # TODO register exit handler to print recipes processed on unexpected exit
        # TODO https://docs.python.org/3/library/atexit.html

        combo_filter = {
            "r": {
                "$gte": self.r_min,
                "$lte": self.r_max
            }
        }

        combination_count = self.combinations.count(combo_filter)
        cursor = self.combinations.find(combo_filter, no_cursor_timeout=True)

        # TODO timeout=False is bad practice
        if self.skip:
            cursor.skip(self.skip)
            processed = self.skip
        else:
            processed = 0

        progress = ProgressBar(combination_count)
        output.push("Counting ors...")
        progress.start()

        BULK_LIMIT = 1000
        bulk = self.combinations.initialize_unordered_bulk_op()
        for combination in cursor:

            combo_id = combination['_id']
            ingredients = combination['ingredients']

            # see https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle
            or_count = 0
            add_sub = 1
            for r in range(1, len(ingredients) + 1):
                combinations = itertools.combinations(ingredients, r)
                for c in combinations:
                    c_id = '::'.join(c)
                    and_count = self.get_and_count_by_id(c_id)
                    or_count += and_count * add_sub
                add_sub *= -1

            bulk.find({"_id": combo_id}).update(
                {
                    "$set": {
                        "or_count": or_count,
                        "score": float(combination['and_count']) / or_count
                    }
                }
            )

            processed += 1

            if processed % BULK_LIMIT == 0:
                # TODO handle bulk execute errors
                progress.update(processed)
                bulk.execute()
                bulk = self.combinations.initialize_unordered_bulk_op()

        progress.update(processed)
        bulk.execute()
        cursor.close()
        progress.end()

    # 2 billion is too big for current settings
    # lru cache with max size of 1 billion
    @functools.lru_cache(1 * 10**9)
    def get_and_count_by_id(self, combo_id):
        return self.combinations.find_one({"_id": combo_id})['and_count']
