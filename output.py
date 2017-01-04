import sys


def push(message):
    sys.stdout.write("{message}\n".format(message=message))
    sys.stdout.flush()


def dynamic_push(message):
    sys.stdout.write("\r{message}".format(message=message))
    sys.stdout.flush()
