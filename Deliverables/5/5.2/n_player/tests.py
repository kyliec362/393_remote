import unittest
from board import set_board_length
from board import get_board_length
from board import board
from n_player import n_player


class PlayerTests(unittest.TestCase):

    def setUp(self):
        self.n_player = n_player("B")
        self.n_player.register_flag = True
        self.n_player.receive_flag = True

    def test_make_capture_1_move(self):
        set_board_length(4)
        board = [["W", "B", " ", " "],
                 [" ", " ", " ", " "],
                 [" ", " ", " ", " "],
                 [" ", "B", "W", "B"]]
        self.assertTrue(self.n_player.make_capture_1_move(board, self.n_player.stone, "1-2"))
        self.assertFalse(self.n_player.make_capture_1_move(board, self.n_player.stone, "2-2"))
        self.assertTrue(self.n_player.make_capture_1_move(board, self.n_player.stone, "3-3"))
        self.assertFalse(self.n_player.make_capture_1_move(board, self.n_player.stone, "1-1"))

    def test_next_player_move(self):
        self.assertEqual(...)

    # def test_randomize_next_move(self):
    #     self.assertEqual(...)
    #
    # def test_make_capture_n_moves(self):
    #     self.assertEqual(...)
    #
    def test_make_a_move(self):
        set_board_length(4)
        test_boards1 = [[["B", "W", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "]],
                        [["B", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "]],
                        [[" ", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "]]]

        print(self.n_player.make_a_move(test_boards1))

        #
        # self.assertEqual(...)


if __name__ == "__main__":
    unittest.main()

