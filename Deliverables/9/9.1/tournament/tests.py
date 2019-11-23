import unittest
from tournament import Cup

# !!! remember to change board size to 4 for testing !!! #

empty = " "
black = "B"
white = "W"
crazy = "GO has gone crazy!"
history = "This history makes no sense!"

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

board3 = [[" ", "S", " ", " "],
          [" ", " ", " ", " "],
          [" ", " ", " ", " "],
          [" ", " ", " ", " "]]


class TournamentTests(unittest.TestCase):

    def setUp(self):
        pass

    # test single board in history
    def test_get_round_indices(self):
        c = Cup()
        print("\n--0--")
        c.get_round_indices(0)
        print("\n--1--")
        c.get_round_indices(1)
        print("\n--2--")
        c.get_round_indices(2)
        #print(c.get_round_indices(0))
        #print(c.get_round_indices(1))
        #print(c.get_round_indices(2))


if __name__ == "__main__":
    unittest.main()
