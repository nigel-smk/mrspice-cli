import time
import output


class ProgressBar:

    def __init__(self, total_count):
        self.total_count = total_count
        self.message = "{percent:04.2f}% | Est. remaining: {remaining} | Elapsed: {elapsed} | Est. Total: {total}"
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def update(self, processed_count):
        # TODO raise not started error
        elapsed = time.time() - self.start_time
        percent = (float(processed_count) / self.total_count) * 100
        remaining = (float(elapsed) / processed_count) * (self.total_count - processed_count)
        total = elapsed + remaining
        output.dynamic_push(self.message.format(
            percent=percent,
            remaining=_format_time(remaining),
            elapsed=_format_time(elapsed),
            total=_format_time(total)
        ))

    def end(self):
        output.push("")


def _format_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return "{d:0>2d}:{h:0>2d}:{m:0>2d}:{s:0>2d}".format(d=int(d), h=int(h), m=int(m), s=int(s))
