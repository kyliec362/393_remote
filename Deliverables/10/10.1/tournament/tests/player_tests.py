import sys
sys.path.append('../')
import unittest
from player_pkg import player, proxy_remote_player, AlphaBetaPlayer
from const import *
from test_boards import *

# !!! remember to change board size to 4 for testing !!! #

class PlayerTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_alpha_beta(self):
        ab_player = AlphaBetaPlayer(2)
        self.assertEqual(True, isinstance(ab_player.register(), str))
        self.assertIsNone((ab_player.receive_stones(black)))
        self.assertEqual(ab_player.make_a_move(board_history4), "2-1")



if __name__ == "__main__":
    unittest.main(warnings='ignore')
