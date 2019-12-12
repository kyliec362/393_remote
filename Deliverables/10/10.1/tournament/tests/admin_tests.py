import unittest
import sys
sys.path.append('../')
from player_pkg.player_file import player, proxy_remote_player
from administrator import administrator

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

class AdminTests(unittest.TestCase):
    def setUp(self):
        self.player1 = player(black, "Kylie")
        self.player2 = player(white, "Micah")
        self.admin = administrator(self.player1, self.player2)

    def setup_game_test(self):
        self.admin.setup_game()
        self.assertEqual(True, True)

    def opposite_wins_test(self):
        self.assertEqual(self.admin.opposite_wins[0], self.player2.name)
        self.admin.referee.swap_player()
        self.assertEqual(self.admin.opposite_wins[0], self.player1.name)

    def get_player_from_name_test(self):
        player1_name = self.player1.name
        player2_name = self.player1.name
        self.assertEqual(self.admin.get_player_from_name(player1_name), self.player1)
        self.assertEqual(self.admin.get_player_from_name(player2_name), self.player2)

    def run_game_test(self):
        self.admin.run_game()
        self.assertEqual(True, True)



if __name__ == "__main__":
    unittest.main()