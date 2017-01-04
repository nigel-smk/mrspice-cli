import time
import output


class CountProgress:

    def __init__(self, total_count):
        self.total_count = total_count
        self.message = "{processed_count} / {total_count} ors counted. Estimated time remaining: {time_remaining}"
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def update(self, processed_count):
        # TODO raise not started error
        elapsed = time.time() - self.start_time
        time_remaining = (float(elapsed) / processed_count) * (self.total_count - processed_count)
        output.dynamic_push(self.message.format(
            processed_count=processed_count,
            total_count=self.total_count,
            time_remaining=_format_time(time_remaining)
        ))

    def end(self):
        output.push("\nCompleted in {elapsed}".format(
            elapsed=_format_time(time.time() - self.start_time)
        ))


def _format_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return "{d:0>2d}:{h:0>2d}:{m:0>2d}:{s:.2f}".format(d=int(d), h=int(h), m=int(m), s=s)
