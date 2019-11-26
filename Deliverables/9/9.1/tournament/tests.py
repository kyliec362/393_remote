import unittest
from tournament import Cup, Tournament, League, RankingInfo
import sys


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

    # def setUp(self):
    #     pass
    #
    # # test single board in history
    # def set_players(self):
    #     sock = Tournament.setup_server()
    #     pass
    #
    # # test single board in history
    # # test with 8 players
    # def test_get_round_indices(self):
    #     c = Cup(8)
    #     self.assertEqual((0, 3), c.get_round_indices(0))
    #     self.assertEqual((4, 5), c.get_round_indices(1))
    #     self.assertEqual((6, 6), c.get_round_indices(2))
    def setUp(self):
        self.league = League(0)
        self.eightArr = [None for i in range(2)]

    def test_generate_schedule(self):
        self.league.generate_schedule()
        print(self.league.schedule)
        self.assertEqual(True, True)


    def test_set_players_names_arr(self):
        self.league.set_players_names_arr()
        print(self.league.players_names_arr)
        self.assertEqual(True, True)

    def test_run_tournament(self):
        print(self.league.run_tournament())

        self.assertEqual(True, True)

# class LeagueTests(unittest.TestCase):
#
#     def setUp(self):
#         self.league = League(8)
#         self.eightArr = [None for i in range(8)]
#
#     def generate_schedule_test(self):
#         print(self.league.generate_schedule(self.eightArr))
#         self.assertEqual(True, True)

if __name__ == "__main__":
    print(83)
    unittest.main(warnings='ignore')
