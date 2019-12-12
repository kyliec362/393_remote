import abc
import sys
import random
import string
sys.path.append('../')
from const import *
from utils import random_string


class Player(abc.ABC):

    def __init__(self,  stone=black, name=random_string()):
        self.stone = stone
        self.name = name
        self.register_flag = False
        self.receive_flag = False
        self.crazy_flag = False
        self.function_names = ['register', 'receive_stones', 'make_a_move', 'end_game']

    def go_crazy(self):
        self.crazy_flag = True
        return crazy

    @abc.abstractmethod
    def make_a_move(self, boards):
        pass

    @abc.abstractmethod
    def register(self):
        pass

    @abc.abstractmethod
    def receive_stones(self, stone):
        pass

    @abc.abstractmethod
    def end_game(self):
        pass