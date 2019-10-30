import unittest
from board import set_board_length
from player import player


class PlayerTests(unittest.TestCase):

    def setUp(self):
        self.player = player("B")
        self.player.register_flag = True
        self.player.receive_flag = True

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
        self.assertEqual(self.player.make_a_move(test_boards1), "1-2")
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
        self.assertEqual(self.player.make_a_move(test_boards2), "This history makes no sense!")
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
        self.assertEqual(self.player.make_a_move(test_boards3), "1-1")
        test_boards4 = [[["B", "W", " ", "B"],
                         ["B", "W", "W", " "],
                         ["B", "B", "B", "W"],
                         ["B", " ", "B", "W"]],
                        [["B", "W", " ", "B"],
                         ["B", "W", "W", " "],
                         ["B", "B", "B", "W"],
                         ["B", " ", "B", "W"]],
                        [["B", "W", " ", " "],
                         ["B", "W", "W", " "],
                         ["B", "B", "B", "W"],
                         ["B", " ", "B", "W"]]]
        self.assertEqual(self.player.make_a_move(test_boards4), "3-1")
        test_boards5 = [[[" ", "W", " ", " "],
                         ["W", " ", " ", " "],
                         ["B", " ", " ", " "],
                         [" ", " ", " ", " "]],
                        [[" ", " ", " ", " "],
                         ["W", " ", " ", " "],
                         ["B", " ", " ", " "],
                         [" ", " ", " ", " "]],
                        [[" ", " ", " ", " "],
                         ["W", " ", " ", " "],
                         [" ", " ", " ", " "],
                         [" ", " ", " ", " "]]]
        self.assertEqual(self.player.make_a_move(test_boards5), "1-4")
        test_boards6 = [[["B", "B", "B", " "],
                         ["B", "W", "B", "B"],
                         [" ", " ", "B", " "],
                         [" ", " ", "B", "B"]],
                        [["B", "B", "B", " "],
                         ["B", " ", "B", "B"],
                         [" ", " ", "B", " "],
                         [" ", " ", "B", "B"]],
                        [["B", "B", "B", " "],
                         [" ", "W", "B", "B"],
                         ["W", "W", "B", " "],
                         ["W", "W", "B", "B"]]]
        self.assertEqual(self.player.make_a_move(test_boards6), "1-3")


if __name__ == "__main__":
    unittest.main()
