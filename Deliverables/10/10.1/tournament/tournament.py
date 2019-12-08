import sys
import abc
from math import log, ceil
import socket
import itertools
import random
import string
import math
from streamy import stream
from board import get_board_length, make_empty_board
from administrator import administrator
from const import *

empty_board = make_empty_board()


# configuration
config_file = open("go.config", "r")
info = list(stream(config_file.readlines()))[0]
default_player_file_path = info["default-player"]
player_pkg = __import__(default_player_file_path)
from player_pkg import proxy_remote_player, player
default_player = player
config_file.close()


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
        sock.listen(5)
        return sock

    def get_num_players(self):
        return self.num_players

    def get_players(self):
        return self.players

    def set_players(self):
        num_joined = 0
        while num_joined < self.num_remote_players:
            try:
                connection, client_address = self.sock.accept()
                connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                new_player = proxy_remote_player(connection)
                self.players.append(new_player)
                self.players_connections[new_player] = connection
                num_joined += 1
            except:
                continue
        self.make_players_power_two()

    def make_players_power_two(self):
        base = 2
        num_players = len(self.players)
        if num_players == 0:
            next_power_two = 2
        else:
            next_power_two = int(pow(base, ceil(log(num_players, base))))
            next_power_two = max(base, next_power_two)
        num_defaults = next_power_two - num_players
        # if somehow something made number default players negative
        if num_defaults < 0:
            num_defaults = 0
        for i in range(num_defaults):
            self.players += [default_player()]
        self.num_players = len(self.players)

    @abc.abstractmethod
    def rank(self):
        pass

    @abc.abstractmethod
    def run_tournament(self):
        pass

    @abc.abstractmethod
    def run_game(self, player1, player2):
        pass

    @abc.abstractmethod
    def close_connections(self):
        pass

class Cup(Tournament):

    def __init__(self, num_remote_players):
        super().__init__(num_remote_players)
        self.remaining_players = self.players
        self.game_outcomes = []
        self.__init_game_outcomes()
        self.win_record = {}
        self.__init_win_record()

    def run_game(self, player1, player2):
        admin = administrator(player1, player2)
        winner_name, cheated = admin.run_game()
        if player1.name == winner_name:
            if cheated:
                return (player1, [player2])
            return (player1, [])
        else:
            if cheated:
                return (player2, [player1])
            return (player2, [])

    def __init_game_outcomes(self):
        self.game_outcomes = [None for i in range(self.num_players - 1)]

    def __init_win_record(self):
        for p in self.players:
            self.win_record[p] = 0

    def run_tournament(self):
        num_rounds = int(log(self.num_players, 2))
        # run though every round in tournament
        for i in range(num_rounds):
            self.__run_round(self.remaining_players, i)
        # get winner
        self.close_connections()
        self.rank()
        self.sock.close()


    def __run_round(self, remaining_players, round_num):
        cheaters = []
        start, end = self.__get_round_indices(round_num)
        if start == end and start == 0:  # only 2 players
            winner, cheater = self.run_game(remaining_players[0], remaining_players[1])
            self.game_outcomes[0] = winner
            cheaters += cheater
        j = 0
        for i in range(start, end + 1):
            winner, cheater = self.run_game(remaining_players[j], remaining_players[j + 1])
            j += 2
            self.game_outcomes[i] = winner
            cheaters += cheater
        self.__eliminate_losers(round_num)
        self.__update_win_record(cheaters)


    def __eliminate_losers(self, round_num):
        start, end = self.__get_round_indices(round_num)
        self.remaining_players = self.game_outcomes[start:end + 1]

    # inclusive indices
    def __get_round_indices(self, round_num):
        games_this_round = int(self.num_players / 2)
        start = 0
        end = games_this_round - 1
        for i in range(round_num):
            games_this_round = int(games_this_round / 2)
            start = end + 1
            end = start + (games_this_round - 1)
        return (start, end)

    def rank(self):
        sorted_ranks = sorted(self.win_record.items(), key=lambda kv: kv[1])
        for key, value in sorted_ranks:
            print("Player : {} , Wins : {}".format(key.name, max(0, value)))

    def __update_win_record(self, cheaters):
        for player in self.remaining_players:
            if player in self.win_record:
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

    def set_players_names_arr(self):
        for i in range(self.num_players):
            self.players_names_arr[i] = self.players[i].name
            self.ranking_info_arr[i].name = self.players_names_arr[i]

    def generate_schedule(self):
        num_players = self.num_players
        indice_player_list = [None for i in range(num_players)]
        for i in range(num_players):
            indice_player_list[i] = i
        combs = itertools.combinations(indice_player_list, 2)
        self.schedule = list(combs)


    def run_tournament(self):
        num_games = int((len(self.players) / 2) * (len(self.players) - 1))
        for i in range(num_games):
            player_one_indice = self.schedule[i][0]
            player_two_indice = self.schedule[i][1]
            player_one = self.players[player_one_indice]
            player_two = self.players[player_two_indice]
            game_dict = self.run_game(player_one, player_two)
            self.handle_game_result(game_dict, player_one_indice, player_two_indice, player_one, player_two)
        return self.rank()

    # return dictionary winner: , loser:, cheater handle tie
    def run_game(self, player1, player2):
        admin = administrator(player1, player2)
        winner_name, cheated = admin.run_game()
        dict_cheater_name = ""
        if cheated:
            dict_cheater_name = self.get_opposite_player_name(player1, player2, winner_name)
        return_dict = {"winner": winner_name, "cheated": dict_cheater_name}
        return return_dict

    def get_opposite_player_name(self, player1, player2, name):
        if name == player1.name:
            return player2.name
        else:
            return player1.name

    def handle_game_result(self, game_dict, p1_indice, p2_indice, p1, p2):
        winner_string = game_dict["winner"][0]
        winner_string = winner_string[1:-1]
        winner = winner_string
        cheater_string = game_dict.get("cheater", "  ")
        cheater_string = cheater_string[1:-1]
        cheater = cheater_string
        if cheater == p1.name:
            self.ranking_info_arr[p2_indice].wins += 1
            self.handle_cheater(p1_indice)
        elif cheater == p2.name:
            self.ranking_info_arr[p1_indice].wins += 1
            self.handle_cheater(p2_indice)
        elif winner == p1.name:
            self.ranking_info_arr[p1_indice].wins += 1
            self.ranking_info_arr[p1_indice].defeated_opponents.append(p2_indice)
            self.ranking_info_arr[p2_indice].losses += 1
        elif winner == p2.name:
            self.ranking_info_arr[p2_indice].wins += 1
            self.ranking_info_arr[p2_indice].defeated_opponents.append(p1_indice)
            self.ranking_info_arr[p1_indice].losses += 1

    def handle_cheater(self, indice):
        ranking_obj = self.ranking_info_arr[indice]
        ranking_obj.wins = 0
        ranking_obj.cheated = True
        cheater_player_name = self.players_names_arr[indice]
        self.cheated_list.extend((cheater_player_name))
        for i in ranking_obj.defeated_opponents:
            self.ranking_info_arr[i].wins += 1
            self.ranking_info_arr[i].losses -= 1
        rand_player_name = random_string()
        self.players[indice] = default_player(name=rand_player_name)
        self.players_names_arr[indice] = rand_player_name
        self.remove_cheater_defeated(indice)
        self.ranking_info_arr[indice] = RankingInfo()
        self.ranking_info_arr[indice].name = rand_player_name

    def remove_cheater_defeated(self, indice):
        for item in self.ranking_info_arr:
            for obj in item.defeated_opponents:
                if obj == indice:
                    item.defeated_opponents.remove(indice)
                    break

    def rank(self):
        ranks_list = self.get_num_ranks()
        ranks_list.sort()
        ranks_list.reverse()
        final_rankings = {}
        for i in ranks_list:
            final_rankings[i] = []
        for rank_info in self.ranking_info_arr:
            final_rankings[rank_info.wins].append(rank_info.name)
        if len(self.cheated_list) > 0:
            final_rankings[-1] = self.cheated_list
            ranks_list.append(-1)
        output_string = "\nFinal Rankings \n"
        for i in range(len(final_rankings)):
            output_string += str(i + 1) + " Place: " + str(final_rankings[ranks_list[i]]) + "\n"
        print(output_string)
        return final_rankings

    def get_num_ranks(self):
        all_wins = [None for i in range(self.num_players)]
        for i in range(len(self.ranking_info_arr)):
            all_wins[i] = self.ranking_info_arr[i].wins
        wins_no_duplicates = []
        [wins_no_duplicates.append(x) for x in all_wins if x not in wins_no_duplicates]
        return wins_no_duplicates

    def get_players_names_arr(self):
        return self.players_names_arr

    def close_connections(self):
        for conn in list(self.players_connections.values()):
            conn.close()


class RankingInfo:
    def __init__(self):
        self.wins = 0
        self.losses = 0
        self.cheated = False
        self.defeated_opponents = []
        self.name = ""


def main():
    cup = 'cup'
    league = "league"
    if len(sys.argv) != 3:
        return
    tournament_style = str(sys.argv[1])
    num_remote_players = int(sys.argv[2])
    if cup in tournament_style:
        c = Cup(num_remote_players)
        c.run_tournament()
    if league in tournament_style:
        l = League(num_remote_players)
        l.run_tournament()



if __name__ == '__main__':
    main()




