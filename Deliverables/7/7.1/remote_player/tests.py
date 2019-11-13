import unittest
from board import set_board_length
from player import proxy_remote_player
from referee import referee

empty = " "
black = "B"
white = "W"


board1a = [[" ", " ", " ", " "],
           [" ", " ", " ", " "],
           [" ", " ", " ", " "],
           [" ", " ", " ", " "]]
board1b = [["B", " ", " ", " "],
           [" ", " ", " ", " "],
           [" ", " ", " ", " "],
           [" ", " ", " ", " "]]
board1c = [["B", " ", " ", " "],
           ["W", " ", " ", " "],
           [" ", " ", " ", " "],
           [" ", " ", " ", " "]]

board_history1 = [board1c, board1b, board1a]

board2d = [["B", "B", "W", "B"],
           ["W", "B", "W", " "],
           ["W", " ", " ", " "],
           ["B", "B", " ", "W"]]
board2c = [["B", "B", "W", "B"],
           ["W", "B", "W", " "],
           ["W", " ", " ", " "],
           ["B", "B", " ", " "]]
board2b = [["B", "B", "W", " "],
           ["W", "B", "W", " "],
           ["W", " ", " ", " "],
           ["B", "B", " ", " "]]
board2a = [["B", "B", "W", " "],
           ["W", "B", "W", " "],
           ["W", " ", " ", " "],
           ["B", "B", " ", " "]]

board_history2 = [board2c, board2b, board2a]


class PlayerTests(unittest.TestCase):

    def setUp(self):
        name = "Micah"
        proxy = proxy_remote_player(black, name)

    # test single board in history
    def test_check_board_object(self):
        # TODO micah
        pass

    # test full board history
    def test_check_boards_object(self):
        # TODO micah
        pass

    def test_make_a_move(self):
        # TODO kylie
        pass

    def test_query(self):
        # TODO kylie
        pass


if __name__ == "__main__":
    unittest.main()
