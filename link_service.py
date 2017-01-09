import output
from repository import Repository
from progress_bar import ProgressBar


class LinkService():

    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.database = kwargs.get('database')

        self.db = Repository(self.host, self.database)
        self.combinations = self.db.get_collection(kwargs.get('combinations'))

    def link(self):
        """exceptions:

        """

        # TODO take r from options if present

        # TODO get max/min r in combinations
        r_max = int(self.combinations.find({}).sort([("r", -1)]).limit(1).next()['r'])
        r_min = int(self.combinations.find({}).sort([("r", 1)]).limit(1).next()['r'])
        records_count = self.combinations.count({
            "r": {
                "$gt": r_min,
                "$lte": r_max
            }
        })

        progress = ProgressBar(records_count)
        processed = 0

        BULK_LIMIT = 1000
        bulk = self.combinations.initialize_unordered_bulk_op()

        output.push("Linking combinations...")
        progress.start()

        cursor = self.combinations.find({
            "r": {
                "$gt": r_min,
                "$lte": r_max
            }
        })
        for combo in cursor:
            ingredients = list(combo['ingredients'])
            combo_id = combo['_id']
            score = combo['score']
            for i in range(len(ingredients)):
                givens = ingredients[:i] + ingredients[i+1:]
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
                            "pairings": {
                                "name": candidate,
                                "score": score,
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
                bulk = self.combinations.initialize_unordered_bulk_op()

        progress.update(processed)
        bulk.execute()
        cursor.close()
        progress.end()
