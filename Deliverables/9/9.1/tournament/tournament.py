import abc
from typing import List
from math import log, ceil
import sys
import socket
import json
from streamy import stream
from board import make_point, board, get_board_length, make_empty_board, parse_point
from referee import referee

# constants
maxIntersection = get_board_length()
empty = " "
black = "B"
white = "W"
n = 1
crazy = "GO has gone crazy!"
history = "This history makes no sense!"
empty_board = make_empty_board()


# configuration
config_file = open("go.config", "r")
info = list(stream(config_file.readlines()))[0]
default_player_file_path = info["default-player"]
player_pkg = __import__(default_player_file_path)
from player_pkg import proxy_remote_player, player
default_player = player


# cup and robin classes implement tournament interface
class Tournament(abc.ABC):

    def __init__(self):
        self.round_number = 0
        self.num_players = 0
        self.set_num_players()
        self.players = []
        self.set_players()
        self.schedule = []
        self.generate_schedule(self.players)
        pass


    def get_num_players(self):
        return self.num_players

    # TODO read from command line args
    def set_num_players(self):
        self.num_players = 8

    def get_players(self):
        return self.players

    def make_players_power_two(self, players: List):
        base = 2
        num_players = len(players)
        next_power_two = int(pow(base, ceil(log(num_players, base))))
        num_defaults = next_power_two - num_players
        for i in range(num_defaults):
            #TODO player should get unique name and not need color set before game starts
            players = players + [default_player(white, "default")]
        return players

    def set_players(self):
        # TODO wait for remote connections
        pass

    @abc.abstractmethod
    def rank(self):
        pass

    @abc.abstractmethod
    #initial schedule
    def generate_schedule(self, players):
        pass

    @abc.abstractmethod
    def get_round_indices(self, round_num):
        pass

    @abc.abstractmethod
    #get round for round robin or next round in single elim
    def get_round(self):
        pass



# single elimination
class Cup(Tournament):

    def __init__(self):
        self.port = info["port"]
        self.ip = info["IP"]

    # TODO can prob just run the game here and return winner to scheduler sca
    def setup_single_game(self, player1, player2):
        pass

    # TODO can abstract to use this to run all the games for single elim
    def generate_schedule(self, players):
        num_players = len(players)
        num_games = num_players - 1
        self.schedule = [None for i in range(num_games)]
        num_games_round_one = int(num_players / 2)
        for i in range(0, num_games_round_one, 2):
            self.schedule[i] = self.setup_single_game(players[i], players[i + 1])

    # TODO finish logic
    def get_round_indices(self, round_num):
        start = 0
        end = start
        num_players = self.num_players
        for i in range(round_num):
            games_this_round = self.num_players / ((i + 1) * 2)
            games_next_found = self.num_players / ((i + 2) * 2)
            start += games_this_round
            end = (start + games_next_found)

        print(start, end)
        return (start, end)




#round robin
class League(Tournament):
    def __init__(self):
        self.port = info["port"]
        self.ip = info["IP"]
        self.win_record = {}


class Schedule(abc.ABC):





