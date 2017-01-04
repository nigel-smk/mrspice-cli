from repository import Repository
from or_count_progress_bar import CountProgress
import itertools
import functools


class OrCountService:

    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.database = kwargs.get('database')

        self.db = Repository(self.host, self.database)
        self.source = self.db.get_collection(kwargs.get('source'))

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

        combination_count = self.source.count(combo_filter)
        cursor = self.source.find(combo_filter, no_cursor_timeout=True)

        # TODO timeout=False is bad practice
        if self.skip:
            cursor.skip(self.skip)
            processed = self.skip
        else:
            processed = 0

        progress = CountProgress(combination_count)
        progress.start()

        BULK_LIMIT = 1000
        bulk = self.source.initialize_unordered_bulk_op()
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
                        "or_count": or_count
                    }
                }
            )

            processed += 1
            progress.update(processed)

            if processed % BULK_LIMIT == 0:
                # TODO handle bulk execute errors
                bulk.execute()
                bulk = self.source.initialize_unordered_bulk_op()

        bulk.execute()
        cursor.close()
        progress.end()

    # lru cache with max size of 2 billion
    @functools.lru_cache(2 * 10**9)
    def get_and_count_by_id(self, combo_id):
        return self.source.find_one({"_id": combo_id})['and_count']
