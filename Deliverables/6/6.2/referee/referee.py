import sys
import json
from streamy import stream
from rule_checker import rule_checker, get_opponent_stone
from board import make_point, board, get_board_length

maxIntersection = get_board_length()
empty = " "
n = 1


class referee:
    def __init__(self, stone):
        pass


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
    # TODO
    for query in lst:
        pass
    print(json.dumps(output))


if __name__ == "__main__":
    main()
