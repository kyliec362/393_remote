import sys
import json
from streamy import stream
from rule_checker import rule_checker, get_opponent_stone
from board import make_point, board, get_board_length

maxIntersection = get_board_length()
empty = " "
n = 1


class n_player:
    def __init__(self, stone, name):
        self.stone = stone
        self.name = name

    def query(self, query_lst):
        # get method and arguments from input query
        method = query_lst[0].replace("-", "_")
        args = query_lst[1:]
        method = getattr(self, method)
        if method:
            return method(*args)
        raise Exception("Not one of the player queries.")


    def make_a_move_dumb(self, boards):
        # don't make a move until a player has been registered with a given stone
        if self.receive_flag and self.register_flag:
            if rule_checker().check_history(boards, self.stone):
                curr_board = boards[0]
                # go through rows and columns to find a point
                # check_validity of that move
                for i in range(maxIntersection):  # row
                    for j in range(maxIntersection):  # col
                        if curr_board[j][i] == empty:
                            point = make_point(i, j)
                            if rule_checker().check_validity(self.stone, [point, boards]):
                                return point
                return "pass"
        return "This history makes no sense!"

    def make_a_move(self, boards):
        # don't make a move until a player has been registered with a given stone
        if rule_checker().check_history(boards, self.stone):
            curr_board = boards[0]
            non_capture_move = None
            # go through rows and columns to find a point
            # check_validity of that move
            for i in range(maxIntersection):  # row
                for j in range(maxIntersection):  # col
                    point = make_point(i, j)
                    if curr_board[j][i] == empty:
                        if rule_checker().check_validity(self.stone, [point, boards]):
                            if self.make_capture_n_moves(n, curr_board, self.stone, point, boards):
                                return point
                            elif non_capture_move is None:
                                non_capture_move = point
            if non_capture_move:
                return non_capture_move
            return "pass"
        return "This history makes no sense!"

    def make_capture_n_moves(self, n, curr_board, stone, point, boards):
        if n == 1:
            return self.make_capture_1_move(curr_board, stone, point)
        new_boards = self.randomize_next_move(n, curr_board, stone, point, boards)
        updated_board = new_boards[0]
        for i in range(maxIntersection):
            for j in range(maxIntersection):
                new_point = make_point(i, j)
                if updated_board[j][i] == empty and rule_checker().check_validity(stone, [new_point, new_boards]):
                    if self.make_capture_1_move(updated_board, stone, new_point):
                        return True
        return False

    def randomize_next_move(self, n, curr_board, stone, point, boards):
        if n == 1:
            return boards
        curr_board = board(curr_board)
        updated_board = curr_board.place(stone, point)
        new_boards = [updated_board] + boards[:min(2, len(boards))]
        opponent_random_move = self.next_player_move(stone, new_boards)
        if opponent_random_move == "pass":
            new_boards = [new_boards[0]] + [new_boards[0]] + [new_boards[1]]
        else:
            new_boards = [board(new_boards[0]).place(get_opponent_stone(stone), opponent_random_move)] + \
                         [new_boards[0]] + [new_boards[1]]
        point = self.make_a_move_dumb(new_boards)
        return self.randomize_next_move(n - 1, new_boards[0], stone, point, new_boards)

    def next_player_move(self, stone, new_boards):
        next_player = n_player(get_opponent_stone(stone))
        next_player.register_flag = True
        next_player.receive_flag = True
        return next_player.make_a_move_dumb(new_boards)

    def make_capture_1_move(self, curr_board, stone, point):
        curr_board = board(curr_board)
        updated_board = curr_board.place(stone, point)
        stones_to_remove = board(updated_board).get_no_liberties(get_opponent_stone(stone))
        if len(stones_to_remove) > 0:
            return True
        return False


def main():
    """
    Test Driver reads json objects from stdin
    Uses the streamy library to parse
    Queries player
    :return: list of json objects
    """
    output = []
    file_contents = ""  # read in all json objects to a string
    special_json = sys.stdin.readline()
    while special_json:
        file_contents += special_json
        special_json = sys.stdin.readline()
    lst = list(stream(file_contents))  # parse json objects
    # assuming input is correctly formatting,
    # the second item in the second input obj should contain the stone
    stone = lst[1][1]
    curr_player = n_player(stone)
    for query in lst:
        result = curr_player.query(query)
        if result:
            output.append(result)
    print(json.dumps(output))


if __name__ == "__main__":
    main()
