import unittest
from tournament import Cup, Tournament, League, RankingInfo
from player_pkg.player_file import player, proxy_remote_player, AlphaBetaPlayer
from const import *
from test_boards import *

# !!! remember to change board size to 4 for testing !!! #

class PlayerTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_alpha_beta(self):
        ab_player =  AlphaBetaPlayer(black, "kylie", 2)
        self.assertEqual(no_name, ab_player.register())
        self.assertIsNone((ab_player.receive_stones(black)))
        self.assertEqual(ab_player.make_a_move(board_history4), "2-1")



if __name__ == "__main__":
    unittest.main(warnings='ignore')
