import time
import output


class Progress:

    def __init__(self, sample_size):
        self.sample_size = sample_size
        self.message = "{sample_count} / {sample_size} records sampled. Estimated time remaining: {time_remaining}"
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def update(self, sample_count):
        # TODO raise not started error
        elapsed = time.time() - self.start_time
        time_remaining = (float(elapsed) / sample_count) * (self.sample_size - sample_count)
        output.dynamic_push(self.message.format(
            sample_count=sample_count,
            sample_size=self.sample_size,
            time_remaining=_format_time(time_remaining)
        ))

    def end(self):
        output.push("\nCompleted in {elapsed}".format(
            elapsed=_format_time(time.time() - self.start_time)
        ))


def _format_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "{h:0>2d}:{m:0>2d}:{s:.2f}".format(h=int(h), m=int(m), s=s)
