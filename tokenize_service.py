from repository import Repository
from or_count_progress_bar import CountProgress


def tokenize(**kwargs):

    # TODO this process should happen in count_and?

    """exceptions:
    """

    # TODO register exit handler to print recipes processed on unexpected exit
    # TODO https://docs.python.org/3/library/atexit.html

    db = Repository(kwargs['host'], kwargs['database'])
    source = db.get_collection(kwargs['source'])

    r_min = int(kwargs["r_min"])
    r_max = int(kwargs["r_max"])

    combo_filter = {
        "r": {
            "$gte": r_min,
            "$lte": r_max
        }
    }

    combination_count = source.count(combo_filter)
    cursor = source.find(combo_filter, no_cursor_timeout=True)
    # TODO timeout=False is bad practice

    if kwargs['skip']:
        cursor.skip(kwargs['skip'])
        processed = kwargs['skip']
    else:
        processed = 0

    progress = CountProgress(combination_count)
    progress.start()

    while processed < combination_count:
        combination = cursor.next()

        combo_id = combination['_id']
        ingredients = combo_id.split('::')

        # clean up extra colons
        ingredients = [i.strip(':') for i in ingredients]

        source.update_one(
            {"_id": combo_id},
            {
                "$set": {
                    "ingredients": ingredients
                }
            }
        )

        processed += 1
        progress.update(processed)

    cursor.close()
    progress.end()
