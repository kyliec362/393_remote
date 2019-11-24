import abc
from typing import List
from math import log, ceil
import sys
import socket
import json
from streamy import stream
from board import make_point, board, get_board_length, make_empty_board, parse_point
from referee import referee
from itertools import combinations

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
        self.players_connections = {}
        self.set_players()
        self.schedule = []
        self.generate_schedule(self.players)



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
        self.num_players = len(self.players)
        self.ranking_info_arr = [RankingInfo for i in range(len(self.players))]
        self.players_names_arr = [None for i in range(self.num_players)]
        self.set_players_names_arr()
        self.cheated_list = []



    # TODO format output
    def rank(self):
        ranks_list = self.get_num_ranks()
        ranks_list.sort()
        ranks_list.reverse()
        final_rankings = [List for i in range(len(ranks_list))]
        for i in range(len(self.ranking_info_arr)):
            item = self.ranking_info_arr[i]
            for j in range(len(ranks_list)):
                if item.wins == ranks_list[j]:
                    final_rankings[j].extend(self.players_names_arr[i])
        if len(self.cheated_list) > 0:
            final_rankings.extend(self.cheated_list)
        return final_rankings


    def get_num_ranks(self):
        all_wins = [None for i in range(self.num_players)]
        count = 0
        for item in self.ranking_info_arr:
            all_wins[count] = item.wins
            count = count + 1
        wins_no_duplicates = []
        [wins_no_duplicates.append(x) for x in all_wins if x not in wins_no_duplicates]
        return wins_no_duplicates



    def generate_schedule(self, players):
        num_players = len(players)
        num_games = int((num_players / 2) * (num_players - 1))
        indice_player_list = [None for i in range(num_players)]
        for i in range(num_players):
            indice_player_list[i] = i
        combs = combinations(indice_player_list, 2)
        self.schedule = [None for i in range(num_games)]
        for i in range (num_games):
            self.schedule[i] = combs.next()


    def set_players_names_arr(self):
        for i in range(self.num_players):
            self.players_names_arr[i] = self.players[i].name
            #self.ranking_info_arr[i].name = self.players[i].name

    def get_players_names_arr(self):
        return self.players_names_arr

    # TODO can prob just run the game here and return winner to scheduler sca
    # return dictionary winner: , loser:, cheater handle tie
    def setup_single_game(self, player1, player2):
        pass

    def handle_game_result(self, game_dict, p1_indice, p2_indice, p1, p2):
        if game_dict["cheated"] == p1.name:
            self.ranking_info_arr[p2_indice].wins += 1
            self.handle_game_result(p1.name, p1_indice)
        elif game_dict["cheated"] == p2.name:
            self.ranking_info_arr[p1_indice].wins += 1
            self.handle_game_result(p2.name, p2_indice)
        elif game_dict["winner"] == p1.name:
            self.ranking_info_arr[p1_indice].wins += 1
            self.ranking_info_arr[p1_indice].defeated_opponents.extend(p2_indice)
            self.ranking_info_arr[p2_indice].losses += 1
        elif game_dict["winner"] == p2.name:
            self.ranking_info_arr[p2_indice].wins += 1
            self.ranking_info_arr[p2_indice].defeated_opponents.extend(p1_indice)
            self.ranking_info_arr[p1_indice].losses += 1

    def handle_cheater(self, indice):
        ranking_obj = self.ranking_info_arr[indice]
        ranking_obj.wins = 0
        ranking_obj.cheated = True
        for i in ranking_obj.defeated_opponents:
            self.ranking_info_arr[i].wins += 1
            self.ranking_info_arr[i].losses -= 1
        self.players[indice] = default_player
        self.players_names_arr[indice] = default_player
        self.cheated_list.extend(ranking_obj)
        self.remove_cheater_defeated(indice)
        self.ranking_info_arr[indice] = RankingInfo

    def remove_cheater_defeated(self, indice):
        for item in self.ranking_info_arr:
            for obj in item.defeated_opponents:
                if obj == indice:
                    item.defeated_opponents.remove(indice)
                    break


    def play_schedule(self, players):
        num_games = int((len(self.players) / 2) * (len(self.players) - 1))
        for i in range (num_games):
            player_one_indice = self.schedule[i][0]
            player_two_indice = self.schedule[i][1]
            player_one = self.players[player_one_indice]
            player_two = self.players[player_two_indice]
            game_dict = self.setup_single_game(player_one, player_two)
            self.handle_game_result(game_dict, player_one_indice, player_two_indice, player_one, player_two)
        self.rank()


    # need only if need to make it pretty
    # #used to generate all the game sets
    # def generate_game_player_matches(self, num_players):
    #     indice_player_list = [None for i in range(num_games)]
    #     for i in range(num_players):
    #         indice_player_list[i] = i
    #     schedule_indices_unsorted = combinations(indice_player_list)
    #     # could do something here to make the rounds pretty but don't think i absolutely need to
    #     # schedule_indices_sorted = [None for i in range(schedule_indices_unsorted)]
    #     # for i in range(len(schedule_indices_unsorted)):




    def get_round(self):
        return self.round_number

    def get_round_indices(self, round_num):
        games_per_round = int(len(self.players) / 2)
        starting_indice = games_per_round * round_num
        ending_indice = games_per_round + (games_per_round * round_num)
        return [starting_indice, ending_indice]


class RankingInfo:
    def _init_(self):
        self.wins = 0
        self.losses = 0
        self.cheated = False
        self.defeated_opponents = []
        self.name



class Schedule(abc.ABC):





