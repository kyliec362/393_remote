import sys
import json
from streamy import stream
import copy
import unittest

# number of rows/columns on Go board
maxIntersection = 4
empty = " "
black = "B"
white = "W"

def make_empty_board():
    col = []
    for i in range(maxIntersection):
        row = []
        for j in range(maxIntersection):
            row += [" "]
        col.append(row)
    return col


# here to resize board for testing purposes
def set_board_length(n):
    global maxIntersection
    maxIntersection = n


def get_board_length():
    return maxIntersection


"""
:param point string representation of a point
:returns list of two representating the row and column of the board intersection
"""
def parse_point(point):
    point = point.split("-")
    temp = int(point[0])
    point[0] = int(point[1])
    point[1] = temp
    if len(point) > 2 or point[0] > maxIntersection or point[1] > maxIntersection or point[0] < 1 or point[1] < 1:
        raise Exception("Invalid point")
    point[0] -= 1
    point[1] -= 1
    return point


"""
:param: row non-negative integer representating row coordinate 
:param: column non-negative integer representing column coordinate
:returns: list of two representating the row and column of the board intersection
"""
def make_point(row, col):
    return str(row + 1) + "-" + str(col + 1)


"""
:param: point list of 2 for row and col coordinates 
:returns: boolean whether coordinates are out of the game board bounds
"""
def out_of_bounds(point):
    return point[0] > (maxIntersection - 1) or point[1] > (maxIntersection - 1) or point[0] < 0 or point[1] < 0


class board:
    def __init__(self, input_board):
        self.game_board = input_board  # assumed already populated right

    """
    :param: query_lst list containing method name and method parameters
    :returns: Result of method call provided in query input
    """
    def query(self, query_lst):
        # get method and arguments from input query
        method = query_lst[0].replace("?", "")
        method = method.replace("-", "_")
        args = query_lst[1:]
        method = getattr(self, method)
        if method:
            return method(*args)
        raise Exception("Not one of the board queries.")

    """
    :param: point list of 2 for row and col coordinates
    :returns: a maybe-stone ("B", "W", or " ") of who is at the provided coordinates
    """
    def get_occupant(self, point):
        return self.game_board[point[0]][point[1]]

    """
    :param: point string representation of coordinates
    :returns: boolean if a stone is at a given point
    """
    def occupied(self, point):
        point = parse_point(point)
        if self.get_occupant(point) != empty:
            return True
        return False

    """
    :param: stone black or white game piece
    :param: point string representation of coordinates
    :returns: boolean if that stone is at a given point
    """
    def occupies(self, stone, point):
        point = parse_point(point)
        return stone == self.get_occupant(point)

    """
    :param: point list of 2 for row and col coordinates
    :param: maybe-stone occupant we want to try to reach
    :return: boolean if we can reach the maybe-stone along a path of the starting point color from the starting point
    """
    def reachable(self, point, maybe_stone):
        seen = set()

        def reachable_helper(path_color, point, maybe_stone, direction):
            # if we are out of bounds, don't even look at the space
            if out_of_bounds(point):
                return False

            # check if we have reached that spot already
            if tuple(point) in seen:
                return False
            seen.add(tuple(point))

            # if we are at the destination (occupant is maybe_stone)
            if maybe_stone == self.get_occupant(point):
                return True

            # If we diverted from the path (the position we are at doesn't match the path color)
            if path_color != self.get_occupant(point):
                return False

            # recurse by exploring other directions for the destination maybe_stone
            # make sure to check previous direction to avoid going back where we came from
            if direction != "down" and reachable_helper(path_color, [point[0] - 1, point[1]], maybe_stone, "up"):
                return True
            if direction != "up" and reachable_helper(path_color, [point[0] + 1, point[1]], maybe_stone, "down"):
                return True
            if direction != "left" and reachable_helper(path_color, [point[0], point[1] + 1], maybe_stone, "right"):
                return True
            if direction != "right" and reachable_helper(path_color, [point[0], point[1] - 1], maybe_stone, "left"):
                return True

            return False

        point = parse_point(point)
        return reachable_helper(self.get_occupant(point), point, maybe_stone, "")

    """
    :param: stone black or white game piece
    :param: point string representation of coordinates
    :returns: list of lists of updated game board or failure message)
    """
    def place(self, stone, point):
        point = parse_point(point)
        occupant = self.get_occupant(point)
        if occupant == empty:
            updated_board = copy.deepcopy(self.game_board)
            updated_board[point[0]][point[1]] = stone
            return updated_board
        return "This seat is taken!"

    """
    :param: stone black or white game piece
    :param: point string representation of coordinates
    :returns: list of lists of updated game board or failure message)
    """
    def remove(self, stone, point):
        point = parse_point(point)
        occupant = self.get_occupant(point)
        if occupant == stone:
            updated_board = copy.deepcopy(self.game_board)
            updated_board[point[0]][point[1]] = empty
            return updated_board
        return "I am just a board! I cannot remove what is not there!"

    """
    :param: maybe_stone either stone or empty
    :returns: list of sorted points of maybe_stone
    """
    def get_points(self, maybe_stone):
        points = []
        for i in range(len(self.game_board)):  # row
            for j in range(len(self.game_board[i])):  # col
                if self.game_board[i][j] == maybe_stone:
                    points.append(make_point(j, i))
        return sorted(points)

    """
    :returns: all points with no liberties on the board for a given stone/player
    """
    def get_no_liberties(self, stone):
        no_liberties = []
        points = self.get_points(stone)
        for point in points:
            if not self.reachable(point, empty):
                no_liberties.append(point)
        return no_liberties
    
    """
    Removing from the board any stones of their opponent's color that have no liberties
    """
    def capture(self, stone):
        stone_to_remove = self.get_no_liberties(stone)
        for point in stone_to_remove:
            self.game_board = self.remove(stone, point)
        return self.game_board

    def calculate_score(self):
        """
        Calculates the score of each player for a given board
        :return: JSON
        """
        white_score = 0
        black_score = 0
        curr_board = self
        for i in range(len(curr_board.game_board)):  # row
            for j in range(len(curr_board.game_board[i])):  # col
                if curr_board.game_board[i][j] == black:
                    black_score += 1
                elif curr_board.game_board[i][j] == white:
                    white_score += 1
                else:
                    reachable_white = curr_board.reachable(make_point(j, i), white)
                    reachable_black = curr_board.reachable(make_point(j, i), black)
                    # if both white and black can reach it, it is neutral
                    if reachable_black and reachable_white:
                        continue
                    elif reachable_black:
                        black_score += 1
                    elif reachable_white:
                        white_score += 1
        return {"B": black_score, "W": white_score}


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
        output.append(board(query[0]).query(query[1]))
    print(json.dumps(output))


class BoardTests(unittest.TestCase):

    def setUp(self):
        self.game_board = board([[" ", " ", "B", " ", " ", "W", "W", "W", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                  [" ", " ", "W", "W", "W", " ", " ", "W", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                  [" ", " ", "B", " ", "W", " ", " ", "W", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                  [" ", " ", " ", " ", "W", " ", " ", "W", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                  [" ", " ", " ", " ", "W", "W", "W", "W", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                  [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                  [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                  [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                  [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                  [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                  [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                  [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                  [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                  [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                  [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                  [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                  [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                  [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                  [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "]])

    def test_occupies(self):
        self.assertTrue(self.game_board.occupies("W", "5-2"))
        self.assertFalse(self.game_board.occupies("B", "3-10"))
        self.assertTrue(self.game_board.occupies(" ", "19-1"))
        self.assertFalse(self.game_board.occupies("W", "3-1"))

    def test_occupied(self):
        self.assertTrue(self.game_board.occupied("5-3"))
        self.assertFalse(self.game_board.occupied("1-19"))

    def test_reachable(self):
        self.assertTrue(self.game_board.reachable("5-3", "B"))
        self.assertTrue(self.game_board.reachable("9-1", "B"))
        self.assertFalse(self.game_board.reachable("6-2", "B"))
        self.assertTrue(self.game_board.reachable("6-1", "B"))

    def test_place(self):
        self.assertEqual(self.game_board.place("B", "4-1"), [[" ", " ", "B", "B", " ", "W", "W", "W", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", "W", "W", "W", " ", " ", "W", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", "B", " ", "W", " ", " ", "W", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", "W", " ", " ", "W", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", "W", "W", "W", "W", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "]])
        self.assertEqual(self.game_board.place("W", "3-1"), "This seat is taken!")
        self.assertEqual(self.game_board.place("B", "3-1"), "This seat is taken!")

    def test_remove(self):
        self.assertEqual(self.game_board.remove("B", "3-3"), [[" ", " ", "B", " ", " ", "W", "W", "W", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", "W", "W", "W", " ", " ", "W", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", "W", " ", " ", "W", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", "W", " ", " ", "W", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", "W", "W", "W", "W", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                                                              [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "]])
        self.assertEqual(self.game_board.remove("W", "3-3"), "I am just a board! I cannot remove what is not there!")
        self.assertEqual(self.game_board.remove("W", "1-1"), "I am just a board! I cannot remove what is not there!")

    def test_get_points(self):
        self.assertEqual(self.game_board.get_points("W"), ["3-2", "4-2", "5-2", "5-3", "5-4", "5-5", "6-1", "6-5", "7-1", "7-5", "8-1", "8-2","8-3", "8-4", "8-5"])
        self.assertEqual(self.game_board.get_points("B"), ["3-1", "3-3"])
        self.assertEqual(board([["B", " ", "W", "W", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "W", " "],
                              ["B", "B", "W", "W", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "W", "B"],
                              ["B", "B", "W", "W", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "W", "B"],
                              ["B", "B", "W", "W", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "W", "B"],
                              ["B", "B", "W", "W", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "W", "B"],
                              ["B", "B", "W", "W", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "W", "B"],
                              ["B", "B", "W", "W", "W", "B", "W", "B", " ", "B", "W", "B", "W", "B", "W", "B", "W", "W", "B"],
                              ["B", "B", "W", "W", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "W", "B"],
                              ["B", "B", "W", " ", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "W", "B"],
                              ["B", "B", "W", "W", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "W", "B"],
                              ["B", "B", "W", "W", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "W", "B"],
                              ["B", "B", "W", "W", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "W", "B"],
                              ["B", "B", "W", "W", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "W", "B"],
                              ["B", "B", "W", "W", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "W", "B"],
                              ["B", "B", "W", "W", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "W", "B"],
                              ["B", "B", "W", "W", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "W", "B"],
                              ["B", "B", "W", "W", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "W", "B"],
                              ["B", "B", "W", "W", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "W", "B"],
                              ["B", "B", "W", "W", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "B", "W", "W", "B"]]).get_points(" "), ["19-1", "2-1", "4-9", "9-7"])


if __name__ == "__main__":
    main()
    # unittest.main()
