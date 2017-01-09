import output
from repository import Repository
from progress_bar import ProgressBar


class SortService():

    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.database = kwargs.get('database')

        self.db = Repository(self.host, self.database)
        self.combinations = self.db.get_collection(kwargs.get('combinations'))

    def sort_pairings(self):
        """exceptions:

        """

        records_count = self.combinations.count({
            "pairings": {"$gt": []}
        })

        progress = ProgressBar(records_count)
        processed = 0

        BULK_LIMIT = 1000
        bulk = self.combinations.initialize_unordered_bulk_op()

        output.push("Sorting pairings...")
        progress.start()

        cursor = self.combinations.find({
            "pairings": {"$gt": []}
        })
        for combo in cursor:
            combo_id = combo['_id']

            bulk.find(
                {
                    "_id": combo_id
                }
            ).update(
                {
                    "$push": {
                        "pairings": {
                            "$each": [],
                            "$sort": {
                                 "score": -1
                            }
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
