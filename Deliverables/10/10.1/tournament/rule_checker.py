import sys
import json
from streamy import stream
from board import board, make_point, get_board_length
import copy
from const import *

maxIntersection = get_board_length()

def get_legal_moves(boards, stone):
    legal_moves = ["pass"]
    for i in range(maxIntersection):  # row
        for j in range(maxIntersection):  # col
            point = make_point(i, j)
            move = [point, boards]
            if rule_checker().check_valid_move(stone, move):
                legal_moves.append(point)
    return legal_moves



def check_liberties_removed(boards):
    for b in boards:
        curr_board = board(b)
        if len(curr_board.get_no_liberties(black)) > 0 or len(curr_board.get_no_liberties(white)) > 0:
            return False
    return True


def check_first_player(boards, stone):
    if not empty_board(boards[1]):
        return False
    else:
        if stone == black:
            return False
        if len(board(boards[0]).get_points(white)) >= 1:
            return False
        return True


def check_ko_rule(boards):
    if boards[0] == boards[2]:
        return False
    return True


def get_opponent_stone(stone):
    return white if stone == black else black


def check_stone_counts(current_board, previous_board, stone):
    num_stones_current = len(current_board.get_points(stone))
    num_stones_previous = len(previous_board.get_points(stone))
    num_opp_stones_current = len(current_board.get_points(get_opponent_stone(stone)))
    num_opp_stones_previous = len(previous_board.get_points(get_opponent_stone(stone)))
    if (num_stones_current != (num_stones_previous + 1)) or (num_opp_stones_current > num_opp_stones_previous):
        return False
    return True


def invalid_swaps(current_board, previous_board):
    for i in range(maxIntersection):  # row
        for j in range(maxIntersection):  # col
            # if a black was switched to a white or vice versa
            if current_board[i][j] == empty:
                continue
            if get_opponent_stone(current_board[i][j]) == previous_board[i][j]:
                return True
    return False


def empty_board(board):
    for i in range(len(board)):  # row
        for j in range(len(board[i])):  # col
            if board[i][j] != empty:
                return False
    return True


def check_valid_capture(current_board, previous_board, stone):
    point = last_played_point([current_board.game_board, previous_board.game_board], stone)
    if point == "pass" or not point:
        return True
    point = make_point(point[0], point[1])
    updated_board = copy.deepcopy(previous_board).place(stone, point)
    updated_board = board(updated_board).capture(get_opponent_stone(stone))
    return updated_board == current_board.game_board


def last_turn_player(boards, stone):
    """
    Identifies the last player to make a play
    :return: stone
    """
    old_board = board(boards[0])
    older_board = board(boards[1])
    # white pieces on board increased
    if len(old_board.get_points(white)) - len(older_board.get_points(white)) > 0:
        return white
    # black must have previously passed if both previous boards are empty
    if empty_board(older_board.game_board) and empty_board(old_board.game_board):
        return black
    # move was a pass
    if old_board.game_board == older_board.game_board:
        # look for player's turn from previous board
        if len(boards) > 2:
            return get_opponent_stone(last_turn_player(boards[1:], get_opponent_stone(stone)))
        return get_opponent_stone(stone)
    return black


def last_played_point(boards, stone):
    """
    Identifies the last play made
    :return: point or pass
    """
    old_board = boards[0]
    older_board = boards[1]
    for i in range(maxIntersection):  # row
        for j in range(maxIntersection):  # col
            if old_board[i][j] == stone and older_board[i][j] == empty:
                return [j, i]
    if older_board == old_board:
        return "pass"
    return False


class rule_checker:
    def __init__(self):
        pass

    def score_or_validity(self, input_json):
        if len(input_json) == maxIntersection:
            return board(input_json).calculate_score()
        return self.check_validity(input_json[0], input_json[1])

    def check_validity(self, stone, move):
        if move == "pass":
            return True
        boards = move[1]
        # check for valid board history
        if not self.check_history(boards, stone):
            return False
        # check for valid intended move
        return self.check_valid_move(stone, move)

    def check_alternating_turns(self, boards, stone, last_player, last_boards):
        if stone == last_player:
            return False
        if last_player == last_turn_player(last_boards, get_opponent_stone(stone)):
            if empty_board(boards[2]) and last_player == black:
                return False
            if boards[1] == boards[2]:
                return self.valid_between_two_boards(last_player,
                                                     [last_played_point(boards, last_player),
                                                      boards], stone)
            return False
        return True

    def check_history(self, boards, stone):
        """
        Verifies that board history is valid
        :return: Bool
        """
        if len(boards) == 1:
            return empty_board(boards[0]) and stone == black
        # check to see if liberties removed from previous boards
        if not check_liberties_removed(boards):
            return False
        if len(boards) == 2:
            # white can't go first
            if not check_first_player(boards, stone):
                return False
            last_player = last_turn_player(boards, stone)
            return self.valid_between_two_boards(last_player,
                                                 [last_played_point(boards, last_player), boards], stone)
        if len(boards) == 3:
            # ko rule violation
            if not check_ko_rule(boards):
                return False
            # can't go twice in a row
            last_player = last_turn_player(boards, stone)
            last_boards = boards[1:]
            if not self.check_alternating_turns(boards, stone, last_player, last_boards):
                return False
            # check valid move between oldest and middle boards and middle and current board
            return self.valid_between_three_boards(stone, last_player, last_boards, boards)
        # invalid number of boards
        return False

    def valid_between_three_boards(self, stone, last_player, last_boards, boards):
        valid_1_2 = self.valid_between_two_boards(last_player,
                                                  [last_played_point(boards, last_player),
                                                   boards], stone)
        valid_2_3 = self.valid_between_two_boards(last_turn_player(last_boards, get_opponent_stone(stone)),
                                                  [last_played_point(last_boards, last_turn_player(last_boards, get_opponent_stone(stone))),
                                                   last_boards], stone)
        if (last_player == last_turn_player(last_boards, get_opponent_stone(stone))) or (not valid_1_2 or not valid_2_3):
            return False
        return True

    def valid_between_two_boards(self, stone, move, initial_stone):
        """
        Compares two boards and determines if the play between them is valid
        :return: Bool
        """
        if move[0] == "pass":
            return True
        # move is a play
        boards = move[1]
        current_board = board(boards[0])
        previous_board = board(boards[1])
        if not check_valid_capture(current_board, previous_board, stone):
            return False
        if current_board.game_board == previous_board.game_board and stone == initial_stone:
            return False
        if get_opponent_stone(stone) == last_turn_player(boards, stone):
            return False
        # both players can't have an increase in stones on the board
        if not check_stone_counts(current_board, previous_board, stone):
            return False
        if invalid_swaps(current_board.game_board, previous_board.game_board):
            return False
        return True


    def check_valid_move(self, stone, move):
        """
        Determines if the upcoming move is valid
        :return: Bool
        """
        if move == "pass":
            return True
        # move is a play
        point = move[0]
        boards = move[1]
        current_board = board(boards[0])
        # can't place stone at occupied point
        if current_board.occupied(point):
            return False
        if len(boards) == 1:
            return empty_board(current_board.game_board) and stone == black
        if len(boards) == 2:
            old_board = boards[1]
            return empty_board(old_board) and \
                (empty_board(current_board.game_board) or len(current_board.get_points(black)) == 1) and \
                stone == white
        # we have the previous 2 moves
        previous_board = board(boards[1])
        if not check_valid_capture(current_board, previous_board, stone):
            return False
        # 2 consecutive passes ends game
        if boards[0] == boards[1] and boards[1] == boards[2]:
            return False
        # player can't go twice in a row
        if stone == last_turn_player(boards, stone):
            return False
        updated_board = current_board.place(stone, point)
        # suicide rule
        updated_board = board(updated_board).capture(get_opponent_stone(stone))
        # if we can perform suicide, move isn't valid
        if board(updated_board).get_no_liberties(stone):
            return False
        # play doesnt recreate previous board (ko rule)
        if updated_board in boards:
            return False
        return True


def main():
    """
    Test Driver reads json objects from stdin
    Uses the streamy library to parse
    Queries game board
    :return: list of json objects
    """
    output = []
    file_contents = ""  # read in all json objects to a string
    special_json = sys.stdin.readline()
    while special_json:
        file_contents += special_json
        special_json = sys.stdin.readline()
    lst = list(stream(file_contents))  # parse json objects
    for query in lst:
        output.append(rule_checker().score_or_validity(query))
    print(json.dumps(output))


if __name__ == "__main__":
    main()
