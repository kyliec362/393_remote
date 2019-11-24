import abc
from typing import List
from math import log, ceil
import operator
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
# from player_pkg import proxy_remote_player, player
from player_pkg.player_file import player
default_player = player


# cup and robin classes implement tournament interface
class Tournament(abc.ABC):

    def __init__(self):
        self.round_number = 0
        self.num_players = 0
        self.set_num_players()
        self.players = []
        self.set_players()
        self.game_outcomes = []
        self.win_record = {}


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
    def run_games(self, players):
        pass

    @abc.abstractmethod
    def get_round_indices(self, round_num):
        pass



# single elimination
class Cup(Tournament):

    def __init__(self):
        super().__init__()
        self.port = info["port"]
        self.ip = info["IP"]
        self.remaining_players = self.players

    # TODO can prob just run the game here and return winner to scheduler
    # TODO update admin to take two players to give to ref?
    def run_single_game(self, player1, player2):
        #TODO write logic, for now just returning a dummy winner
        return player1

    def init_game_outcomes(self):
        self.game_outcomes = [None for i in range(self.num_players - 1)]

    # TODO can abstract to use this to run all the games for single elim
    def run_games(self, players):
        num_rounds = log(self.num_players, 2)
        for i in range(num_rounds):
            self.run_game(self.remaining_players, i)
        return self.get_tournament_winner()

    def run_game(self, remaining_players, round_num):
        start, end = self.get_round_indices(round_num)
        for i in range(start, end, 2):
            self.game_outcomes[i] = self.run_single_game(remaining_players[i], remaining_players[i + 1])
        self.eliminate_losers(round_num)
        self.rank()

    def eliminate_losers(self, round_num):
        start, end = self.get_round_indices(round_num)
        self.remaining_players = self.game_outcomes[start:(end + 1)]

    # inclusive indices
    def get_round_indices(self, round_num):
        games_this_round = int(self.num_players / 2)
        start = 0
        end = games_this_round - 1
        for i in range(round_num):
            games_this_round = int(games_this_round / 2)
            start = end + 1
            end = start + (games_this_round - 1)
        return (start, end)

    def get_tournament_winner(self):
        return max(self.win_record.items(), key=operator.itemgetter(1))[0]

    # update ranks
    # TODO update to handle cheaters
    def rank(self):
        for player in self.remaining_players:
            self.win_record[player] += 1





#round robin
class League(Tournament):
    def __init__(self):
        self.port = info["port"]
        self.ip = info["IP"]
        self.win_record = {}


# class Schedule(abc.ABC):





