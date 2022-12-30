import os

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH = BASE_PATH + '/storage/data/'
SCREENSHOT_PATH = BASE_PATH + '/storage/screenshots/'
ADDITIONAL_NODE_BUFFER_DATA: int = 6
ADDITIONAL_EDGE_BUFFER_DATA: int = 8


def pairwise(it, size: int):
    it = iter(it)
    while True:
        try:
            yield next(it)
            for _ in range(size - 1):
                next(it)
        except StopIteration:
            return


def vec4wise(it):
    it = iter(it)
    while True:
        try:
            yield next(it), next(it), next(it), next(it),
        except StopIteration:
            return
