import random
import string
from const import *


def random_string():
    """Generate a random string of fixed length """
    length = 5
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def update_board_history(new_board0, boards):
    return [new_board0] + boards[:min(2, len(boards))]


def flip_coin():
    return random.randint(0, 1) == 0

def is_stone(stone):
    return stone == black or stone == white
