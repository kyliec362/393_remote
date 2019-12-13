import sys
import json
from streamy import stream
from board import get_board_length, make_empty_board, parse_point
from referee import referee
from const import *

# configuration
config_file = open("go.config", "r")
info = list(stream(config_file.readlines()))[0]
default_player_file_path = info["default-player"]
player_pkg = __import__(default_player_file_path)
from player_pkg import *
config_file.close()

default_player = player

empty_board = make_empty_board()


class administrator:

    def __init__(self, player1, player2):
        self.player2 = player2
        self.player1 = player1
        self.referee = None

    # tuple of winner and whether the win was a result of cheating
    # (True means there was cheating, False means no cheating)
    def opposite_wins(self):
        return [self.referee.get_opposite_player().name], True

    # checking to see the if the input is pass and if it is then returning true otherwise checking to make sure
    # parse_point is true if so return
    def check_input(self, input):
        if input == "pass":
            return True
        return bool(parse_point(input))

    # calls referee handle move function and if true returns true otherwise says bad move with false
    def referee_move(self, input):
        if self.referee.handle_move(input):
            return True
        return False

    # sets up the game by initializing the referee and calling register and receive for the players
    def setup_game(self):
        self.referee = referee(self.player1, self.player2)
        self.register_receive_player(self.player1, black)
        self.register_receive_player(self.player2, white)

    def register_receive_player(self, p, stone):
        p.register()
        p.receive_stones(stone)

    # if the end game response does not go through switch the winner to the other player because they cheat otherwise
    # return the original winner
    def end_game_update_winner(self, original_winner, cheated):
        ok = "OK"
        original_winner_player = self.get_player_from_name(original_winner)
        original_loser_player = self.referee.get_opposite_player_from_name(original_winner)
        response1 = original_winner_player.end_game()
        original_loser_player.end_game()
        if not cheated and response1 != ok:
            return [json.dumps(original_loser_player.name)], cheated
        return [json.dumps(original_winner_player.name)], cheated

    # given a name return the player associated with that name
    def get_player_from_name(self, name):
        if name == self.player1.name:
            return self.player1
        if name == self.player2.name:
            return self.player2
        else:
            print(name, self.player1.name, self.player2.name)
            raise Exception("Invalid name given")

    # setting up the game and then running it
    def run_game(self):
        self.setup_game()
        return self.referee.current_player.name, False
        # while True:
        #     move = self.referee.current_player.make_a_move(self.referee.board_history)
        #     print(self.referee.current_player.name, move)
        #     if isinstance(move, str):
        #         move = move.replace('"', '')
        #     # if player didn't disconnect while making a move
        #     if move and self.check_input(move):
        #         not_over = self.referee.handle_move(move)
        #         # if the game didn't end, continue to next turn
        #         if not_over:
        #             continue
        #         # game over, figure out the winner
        #         # alert players it's game over (check for disconnects)
        #         original_winner, cheated = self.referee.get_winner()
        #         # get the actual winner
        #         return self.end_game_update_winner(original_winner[0], cheated)
        #     original_winner, cheated = self.opposite_wins()
        #     return self.end_game_update_winner(original_winner[0], cheated)


if __name__ == '__main__':
    pass

