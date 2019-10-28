import sys
import json
from streamy import stream
from rule_checker import rule_checker
from board import make_point

maxIntersection = 19
empty = " "
n = 1


class n_player:
    def __init__(self, stone):
        self.stone = stone
        self.register_flag = False
        self.receive_flag = False

    def query(self, query_lst):
        # get method and arguments from input query
        method = query_lst[0].replace("-", "_")
        args = query_lst[1:]
        method = getattr(self, method)
        if method:
            return method(*args)
        raise Exception("Not one of the player queries.")

    def register(self):
        self.register_flag = True
        return "no name"

    def receive_stones(self, stone):
        self.receive_flag = True
        self.stone = stone

    def make_a_move(self, boards):
        # don't make a move until a player has been registered with a given stone
        if self.receive_flag and self.register_flag:
            if rule_checker().check_history_mam(boards, self.stone):
                curr_board = boards[0]
                capture_moves = []
                # go through rows and columns to find all points that capture
                for i in range(maxIntersection):  # row
                    for j in range(maxIntersection):  # col
                        if rule_checker().make_capture_n_moves(n, curr_board, curr_board[i][j]):
                            capture_moves.append(make_point(i, j))
                # go through the list of points and check validity
                for point in capture_moves:
                    if rule_checker().check_validity(self.stone, [point, boards]):
                        return point
                return "pass"
        return "This history makes no sense!"


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
