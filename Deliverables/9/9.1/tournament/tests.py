import unittest
# from .player_pkg.player_file import player, proxy_remote_player
import sys
sys.path.append("./")
from tournament import Cup, Tournament

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


class PlayerTests(unittest.TestCase):

    def setUp(self):
        pass

    # # test single board in history
    # def set_players(self):
    #     sock = Tournament.setup_server()
    #     pass

    # test single board in history
    # test with 8 players
    def test_get_round_indices(self):
        c = Cup(8)
        self.assertEqual((0, 3), c.get_round_indices(0))
        self.assertEqual((4, 5), c.get_round_indices(1))
        self.assertEqual((6, 6), c.get_round_indices(2))


if __name__ == "__main__":
    unittest.main()
