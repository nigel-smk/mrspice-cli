from common import output

from common.progress_bar import ProgressBar
from repository.repository import Repository


class SortService():

    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.database = kwargs.get('database')
        self.r_min = int(kwargs["r_min"])
        self.r_max = int(kwargs["r_max"])

        self.db = Repository(self.host, self.database)
        self.combinations = self.db.get_collection(kwargs.get('combinations'))

    def sort_pairings(self):
        """exceptions:

        """

        combo_filter = {
            "pairings": {"$gt": []},
            "r": {
                "$gte": self.r_min,
                "$lte": self.r_max
            }
        }

        records_count = self.combinations.count(combo_filter)

        progress = ProgressBar(records_count)
        processed = 0

        BULK_LIMIT = 1000
        bulk = self.combinations.initialize_unordered_bulk_op()

        output.push("Sorting pairings...")
        progress.start()

        cursor = self.combinations.find(combo_filter)
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
