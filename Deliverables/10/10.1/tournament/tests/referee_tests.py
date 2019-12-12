import unittest
from board import set_board_length
from player_pkg.player_file import player, proxy_remote_player, AlphaBetaPlayer
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
        self.player1 = player(black, "Kylie")
        self.player2 = player(white, "Micah")
        self.ref = referee(self.player1, self.player2)

    def test_get_winner(self):
        # test a draw
        self.ref.board_history = board_history1
        self.assertEqual(self.ref.get_winner(), ['Kylie', 'Micah'])
        # test single winner
        self.ref.board_history = board_history2
        self.assertEqual(self.ref.get_winner(), ['Kylie'])

    def test_cheated(self):
        self.ref.board_history = [board1a]
        self.ref.current_player = self.player1
        self.assertEqual(self.ref.cheated(), ['Micah'])

    def test_update_board_history(self):
        # test shorter board history (less than 3)
        self.ref.board_history = [board1a]
        self.ref.current_player = self.player1
        self.ref.handle_move("1-1")
        self.assertEqual(self.ref.board_history, [board1b, board1a])
        # test populated board history (3 boards)
        self.ref.board_history = board_history2
        self.ref.current_player = self.player2
        self.ref.handle_move("4-4")
        self.assertEqual(self.ref.board_history, [board2d, board2c, board2b])
        # test a pass move
        self.ref.board_history = board_history2
        self.ref.current_player = self.player2
        self.ref.handle_move("pass")
        self.assertEqual(self.ref.board_history, [board2c, board2c, board2b])

    def test_swap_player(self):
        self.ref.current_player = self.player1
        self.ref.swap_player()
        self.assertEqual(self.ref.current_player, self.player2)

    def test_handle_move(self):
        self.assertTrue(self.ref.handle_move("pass"))
        self.assertFalse(self.ref.handle_move("pass"))
        ref2 = referee(self.player1, self.player2)
        self.assertTrue(ref2.handle_move("1-1"))
        self.assertTrue(ref2.handle_move("pass"))
        self.assertFalse(ref2.handle_move("1-1"))
        self.assertTrue(ref2.handle_move("pass"))




if __name__ == "__main__":
    unittest.main()