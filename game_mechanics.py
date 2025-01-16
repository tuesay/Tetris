import random

from settings import *

def bag7():
    return sorted(TETROMINOS.keys(), key=lambda x: random.random())

