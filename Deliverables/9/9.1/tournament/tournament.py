import sys
import abc
from typing import List
from math import log, ceil
import operator
import socket
import json
import itertools

import random
import string
import math
from streamy import stream
from board import get_board_length, make_empty_board
from administrator import administrator

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
config_file.close()


def random_string():
    """Generate a random string of fixed length """
    length = 5
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


# cup and robin classes implement tournament interface
class Tournament(abc.ABC):

    def __init__(self, num_remote_players):
        self.port = info["port"]
        self.ip = info["IP"]
        self.sock = self.setup_server()
        self.round_number = 0
        self.num_players = 0
        self.num_remote_players = num_remote_players
        self.players = []
        self.players_connections = {}
        self.set_players()
        self.schedule = []



    def setup_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.ip, self.port))
        sock.settimeout(40)
        sock.listen(1)
        return sock

    def get_num_players(self):
        return self.num_players

    def get_players(self):
        return self.players

    def make_players_power_two(self):
        base = 2
        num_players = len(self.players)
        if num_players <= 0:
            next_power_two = 2
        else:
            next_power_two = int(pow(base, ceil(log(num_players, base))))
            next_power_two = min(base, next_power_two)
        num_defaults = next_power_two - num_players
        for i in range(num_defaults):
            #TODO player should get unique name and not need color set before game starts
            self.players = self.players + [default_player(white, random_string())]
        self.num_players = len(self.players)


    def set_players(self):
        num_joined = 0
        print(90)
        while num_joined < self.num_remote_players:
            try:
                connection, client_address = self.sock.accept()
                new_player = proxy_remote_player(connection, 'B', random_string())  # TODO player shouldnt take in stone
                self.players.append(new_player)
                self.players_connections[new_player] = connection
                num_joined += 1
            except:
                continue
        self.make_players_power_two()
        print(104)

    @abc.abstractmethod
    def rank(self):
        pass

    @abc.abstractmethod
    def run_tournament(self):
        pass

    @abc.abstractmethod
    def close_connections(self):
        pass





# single elimination
class Cup(Tournament):

    def __init__(self, num_remote_players):
        super().__init__(num_remote_players)
        self.remaining_players = self.players
        self.game_outcomes = []
        self.win_record = {}  # TODO replace schedule state var with this

    # TODO When a game finishes your referee should notify both players in a game that the game is over.
    # For remote players this boils down to receiving a message ["end-game"]
    # to which it replies with the JSON string "OK".

    def run_game(self, player1, player2):
        admin = administrator(player1, player2, self.players_connections[player1], self.players_connections[player2])
        winner_name, cheated = admin.run_round()
        if player1.name == winner_name:
            if cheated:
                return (player1, [player2])
            return (player1, [])
        else:
            if cheated:
                return (player2, [player1])
            return (player2, [])

    def init_game_outcomes(self):
        self.game_outcomes = [None for i in range(self.num_players - 1)]

    # TODO dont need players param
    def run_tournament(self):
        num_rounds = int(log(self.num_players, 2))
        # run though every round in tournament
        for i in range(num_rounds):
            self.run_round(self.remaining_players, i)
        # get winner
        self.close_connections()
        self.rank()

    def run_round(self, remaining_players, round_num):
        cheaters = []
        start, end = self.get_round_indices(round_num)
        for i in range(start, end, 2):
            winner, cheater = self.run_game(remaining_players[i], remaining_players[i + 1])
            self.game_outcomes[i] = winner
            cheaters += cheater
        self.eliminate_losers(round_num)
        self.update_win_record(cheaters)

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

    # TODO print all rnakings, not just winner
    def rank(self):
        print(max(self.win_record.items(), key=operator.itemgetter(1))[0])

    def update_win_record(self, cheaters):
        for player in self.remaining_players:
            self.win_record[player] += 1
        for c in cheaters:
            # keep cheaters always with the lowest score
            self.win_record[c] = (-1 * math.inf)

    def close_connections(self):
        for conn in list(self.players_connections.values()):
            conn.close()



#round robin
class League(Tournament):
    def __init__(self, num_remote_players):
        super().__init__(num_remote_players)
        self.port = info["port"]
        self.ip = info["IP"]
        self.num_players = len(self.players)
        self.ranking_info_arr = [RankingInfo() for i in range(len(self.players))]
        self.players_names_arr = [None for i in range(self.num_players)]
        self.set_players_names_arr()
        self.cheated_list = []
        self.generate_schedule()

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
        outputString = "Final Rankings \n"
        for i in range(len(final_rankings)):
            outputString += str(i) + " Place: "
            tied_list = final_rankings[i]
            for j in range(len(tied_list)):
                outputString += final_rankings[i][j]
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
        combs = itertools.combinations(indice_player_list, 2)
        self.schedule = list(combs)
        # self.schedule = [None for i in range(num_games)]
        # for i in range (num_games):
        #     self.schedule[i] = combs.next()

    def set_players_names_arr(self):
        for i in range(self.num_players):
            self.players_names_arr[i] = self.players[i].name
            # self.ranking_info_arr[i].name = self.players[i].name

    def get_players_names_arr(self):
        return self.players_names_arr

    def get_opposite_player_name(self, player1, player2, name):
        if name == player1.name:
            return player2.name
        else:
            return player1.name

    # TODO can prob just run the game here and return winner to scheduler sca
    # return dictionary winner: , loser:, cheater handle tie
    def setup_single_game(self, player1, player2):
        admin = administrator(player1, player2, self.players_connections[player1], self.players_connections[player2])
        winner_name, cheated = admin.run_game()
        dict_cheater_name = ""
        if cheated:
            dict_cheater_name = self.get_opposite_player_name(player1, player2, winner_name)
        return_dict = {"winner": winner_name, "cheated": dict_cheater_name}
        return return_dict

    def handle_game_result(self, game_dict, p1_indice, p2_indice, p1, p2):
        if game_dict["cheated"] == p1.name:
            self.ranking_info_arr[p2_indice].wins += 1
            self.handle_cheater(p1_indice)
        elif game_dict["cheated"] == p2.name:
            self.ranking_info_arr[p1_indice].wins += 1
            self.handle_cheater(p2_indice)
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
        self.ranking_info_arr[indice] = RankingInfo()

    def remove_cheater_defeated(self, indice):
        for item in self.ranking_info_arr:
            for obj in item.defeated_opponents:
                if obj == indice:
                    item.defeated_opponents.remove(indice)
                    break

    def run_tournament(self):
        num_games = int((len(self.players) / 2) * (len(self.players) - 1))
        for i in range(num_games):
            player_one_indice = self.schedule[i][0]
            player_two_indice = self.schedule[i][1]
            player_one = self.players[player_one_indice]
            player_two = self.players[player_two_indice]
            game_dict = self.setup_single_game(player_one, player_two)
            self.handle_game_result(game_dict, player_one_indice, player_two_indice, player_one, player_two)
        return self.rank()

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

    def close_connections(self):
        for conn in list(self.players_connections.values()):
            conn.close()


class RankingInfo:
    def _init_(self):
        self.wins = 0
        self.losses = 0
        self.cheated = False
        self.defeated_opponents = []
        #self.name



def main():
    cup = 'cup'
    league = "league"
    tournament_style = str(sys.argv[1])[1:]
    num_remote_players = int(sys.argv[2])
    if tournament_style == cup:
        c = Cup(num_remote_players)
        c.run_tournament()
    if tournament_style == league:
        l = League(num_remote_players)
        l.run_tournament() # TODO change to run tournament



if __name__ == '__main__':
    main()




