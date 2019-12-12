from rule_checker import rule_checker, get_opponent_stone
from board import make_point, board, get_board_length, make_empty_board
from player_pkg.Player import Player
from const import *
from utils import update_board_history, flip_coin

empty_board = make_empty_board()


class referee:
    def __init__(self, player1, player2):
        self.player_count = 0
        self.player1 = player1
        self.player2 = player2
        if isinstance(player1, Player) and isinstance(player2, Player):
            self.player_count = players_per_game
        self.pass_count = 0
        self.board_history = [empty_board]
        self.current_player = player1
        self.game_output = [black, white]

    def swap_player(self):
        self.current_player = self.get_opposite_player()

    def get_opposite_player(self):
        if self.current_player == self.player1:
            return self.player2
        else:
            return self.player1

    def get_opposite_player_from_name(self, name):
        if name == self.player1.name:
            return self.player2
        else:
            return self.player1


    # returns true if game should continue, false if not
    def handle_move(self, input):
        self.game_output.append(self.board_history)
        if input == "pass":
            if self.pass_count == 1:
                self.game_output.append(self.get_winner())
                return False
            self.update_board_history(self.board_history[0])
            self.pass_count += 1
            self.swap_player()
            return True
        stone = self.current_player.stone
        move = [input, self.board_history]
        if rule_checker().check_validity(stone, move):
            new_board0 = board(self.board_history[0]).place(stone, input)
            new_board0 = board(new_board0).capture(get_opponent_stone(stone))
            self.update_board_history(new_board0)
            self.pass_count = 0
            self.swap_player()
            return True
        else:
            self.game_output.append(self.cheated())
            return False

    def update_board_history(self, new_board0):
        self.board_history = update_board_history(new_board0, self.board_history)

    # returns winner if someone current player cheated
    def cheated(self):
        self.swap_player()
        return [self.current_player.name]

    def get_winner(self):
        scores = board(self.board_history[0]).calculate_score()
        black_score = scores[black]
        white_score = scores[white]
        # draw
        if black_score == white_score:
            if flip_coin():
                return [self.player1.name], False
            return [self.player2.name], False
        # player1 is always black
        if black_score > white_score:
            return [self.player1.name], False  # win wasn't due to cheating
        return [self.player2.name], False  # win wasn't due to cheating


def main():
    pass


if __name__ == "__main__":
    main()
