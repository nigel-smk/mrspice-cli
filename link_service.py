from repository import Repository
from progress_bar import ProgressBar


class LinkService():

    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.database = kwargs.get('database')

        self.db = Repository(self.host, self.database)
        self.source = self.db.get_collection(kwargs.get('source'))

    def link(self):
        """exceptions:

        """

        # TODO take r from options if present

        # TODO get max/min r in combinations
        r_max = int(self.source.find({}).sort([("r", -1)]).limit(1).next()['r'])
        r_min = int(self.source.find({}).sort([("r", 1)]).limit(1).next()['r'])
        records_count = self.source.count({
            "r": {
                "$gt": r_min,
                "$lte": r_max
            }
        })

        progress = ProgressBar(records_count, "combinations linked")
        processed = 0

        BULK_LIMIT = 1000
        bulk = self.source.initialize_unordered_bulk_op()

        progress.start()
        # link the largest combinations first
        for r in range(r_max, r_min, -1):
            cursor = self.source.find({"r": r})
            for combo in cursor:
                ingredients = list(combo['ingredients'])
                combo_id = combo['_id']
                for i in range(len(ingredients)):
                    givens = ingredients[:i] + ingredients[i:]
                    candidate = ingredients[i]

                    givens.sort()
                    givens_combo_id = "::".join(givens)
                    bulk.find(
                        {
                            "_id": givens_combo_id
                        }
                    ).update(
                        {
                            "$addToSet": {
                                "links": {
                                    "candidate": candidate,
                                    "ref_id": combo_id
                                }
                            }
                        }
                    )

                processed += 1
                if processed % BULK_LIMIT == 0:
                    progress.update(processed)
                    # TODO handle bulk execute errors
                    bulk.execute()
                    bulk = self.source.initialize_unordered_bulk_op()

        bulk.execute()
        cursor.close()
        progress.end()
