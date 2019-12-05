import unittest
from player_pkg.player_file import player, proxy_remote_player, AlphaBetaPlayer
from const import *
from test_boards import *
from tournament import Tournament, League, Cup


class TournamentTests(unittest.TestCase):

    def setUp(self):
        self.league = League(0)
        self.eightArr = [None for i in range(2)]

    def test_generate_schedule(self):
        self.league.generate_schedule()
        self.assertEqual(True, True)

    def test_set_players_names_arr(self):
        self.league.set_players_names_arr()
        self.assertEqual(True, True)

    def test_run_tournament(self):
        self.league.run_tournament()
        self.assertEqual(True, True)

    def test_cup_default(self):
        c = Cup(0)
        self.assertIsNone(c.run_tournament()) # should run without errors
        c = Cup(-1)
        self.assertIsNone(c.run_tournament())  # should run without errors, since negatives changed to 2 defaults

    def test_make_power_two(self):
        c = Cup(0)
        c.players = [player(white, "test") for i in range(7)]
        c.make_players_power_two()
        self.assertEqual(8, len(c.players))


if __name__ == "__main__":
    unittest.main(warnings='ignore')