import unittest
from board import set_board_length
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
        set_board_length(4)
        board = [[" ", " ", " ", " "],
                 [" ", " ", " ", " "],
                 [" ", " ", " ", " "],
                 [" ", " ", " ", " "]]
        board2 = [["B", " ", " ", " "],
                  [" ", " ", " ", " "],
                  [" ", " ", " ", " "],
                  [" ", " ", " ", " "]]
        board3 = [["B", " ", " ", " "],
                  ["W", " ", " ", " "],
                  [" ", " ", " ", " "],
                  [" ", " ", " ", " "]]
        full_boards = [[["B", "B", "W", "B"],
                        ["W", "B", "W", " "],
                        ["W", " ", " ", " "],
                        ["B", "B", " ", " "]],
                       [["B", "B", "W", " "],
                        ["W", "B", "W", " "],
                        ["W", " ", " ", " "],
                        ["B", "B", " ", " "]],
                       [["B", "B", "W", " "],
                        ["W", "B", "W", " "],
                        ["W", " ", " ", " "],
                        ["B", "B", " ", " "]]]
        self.assertEqual("1-1", self.n_player.next_player_move("W", [board]))
        self.assertEqual("1-2", self.n_player.next_player_move("B", [board2] + [board]))
        self.assertEqual("1-3", self.n_player.next_player_move("W", [board3, board2, board]))
        self.assertEqual("2-3", self.n_player.next_player_move("B", full_boards))
        self.assertEqual("This history makes no sense!", self.n_player.next_player_move("W", full_boards))

    def test_randomize_next_move(self):
        set_board_length(4)
        start_boards = [[[" ", "B", "W", "B"],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "]],
                        [[" ", "B", "", "B"],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "]],
                        [[" ", "B", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "]]]
        final_boards = [[["B", "B", "W", "B"],
                         ["W", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "]],
                        [["B", "B", "W", "B"],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "]],
                        [[" ", "B", "W", "B"],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "]]]
        self.assertEqual(start_boards, self.n_player.randomize_next_move(1, start_boards[0], self.n_player.stone,
                                                                         "1-1", start_boards))
        self.assertEqual(final_boards, self.n_player.randomize_next_move(2, start_boards[0], self.n_player.stone,
                                                                         "1-1", start_boards))

    def test_make_capture_n_moves(self):
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
        self.assertEqual(self.n_player.make_capture_n_moves(1, test_boards1[0], self.n_player.stone, "2-2", test_boards1), False)
        test_boards2 = [[["W", "W", "W", " "],
                         ["W", "W", "W", " "],
                         ["B", " ", " ", " "],
                         [" ", " ", " ", " "]],
                        [["W", "W", "W", " "],
                         ["W", " ", "W", " "],
                         ["B", " ", "B", " "],
                         [" ", " ", " ", " "]],
                        [["W", "W", "W", " "],
                         ["W", " ", "W", " "],
                         ["B", " ", " ", " "],
                         [" ", " ", " ", " "]]]
        self.assertEqual(self.n_player.make_capture_n_moves(1, test_boards2[0], self.n_player.stone, "1-4", test_boards2), False)

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
        self.assertEqual(self.n_player.make_a_move(test_boards1), "1-2")
        test_boards2 = [[["B", "W", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "]],
                        [[" ", "W", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "]],
                        [[" ", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "]]]
        self.assertEqual(self.n_player.make_a_move(test_boards2), "This history makes no sense!")
        test_boards3 = [[[" ", "W", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "]],
                        [[" ", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "]],
                        [[" ", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "]]]
        self.assertEqual(self.n_player.make_a_move(test_boards3), "1-1")

if __name__ == "__main__":
    unittest.main()
