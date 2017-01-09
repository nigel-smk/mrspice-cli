from repository import Repository
from progress_bar import ProgressBar
import random
import re


def sample_collection(**kwargs):
    """exceptions:
        fewer records than sample size
        sample size not an integer
        source does not exist
        destination already exists
        database connection exceptions
    """
    db = Repository(kwargs['host'], kwargs['database'])
    source = db.get_collection(kwargs['source'])
    destination = db.get_collection(kwargs['destination'])
    # TODO pass filter in from json file
    doc_filter = {'attributes': {'$gt': {}}, 'attributes.course': {'$nin': ['Desserts', 'Cocktails', 'Beverages']}}

    if doc_filter:
        record_count = source.count(doc_filter)
    else:
        record_count = source.count()
    seed = kwargs['seed']
    sample_size = parse_number(kwargs['size'])

    random.seed(seed)
    to_sample = random.sample(range(0, record_count), sample_size)
    to_sample.sort()

    progress = ProgressBar(sample_size)
    progress.start()

    if doc_filter:
        cursor = source.find(doc_filter)
    else:
        cursor = source.find()

    sample_count = 0
    position = 0
    for index in to_sample:
        while position <= index:
            record = cursor.next()
            position += 1
        # TODO batch insert?
        destination.insert_one(record)
        sample_count += 1
        progress.update(sample_count)

    progress.end()


def parse_number(n):
    zeroes_map = {
        'k': 10**3,
        'm': 10**6,
        'b': 10**9,
        't': 10**12
    }

    match = re.match(r"\b([0-9]+)([k,m,b,t]?)\b", n, re.IGNORECASE)
    if match:
        number, letter = match.groups()
        return int(number) * zeroes_map[letter] if letter else int(number)
    else:
        pass
        # raise sizeError