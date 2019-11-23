import unittest
from board import set_board_length
from player import proxy_remote_player

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
        self.name = "Micah"

    # test single board in history
    def test_check_board_object(self):
        # TODO micah
        pass

    # test full board history
    def test_check_boards_object(self):
        # TODO micah
        pass

    def test_make_a_move(self):
        proxy = proxy_remote_player(black, self.name)
        proxy.player.register_flag = True
        proxy.player.receive_flag = True
        self.assertEqual(proxy.player.make_a_move(board_history2), history)
        self.assertEqual(proxy.player.make_a_move(board_history1), "1-3")
        self.assertEqual(proxy.player.make_a_move([board1a, board1a, board1a, board1a]), crazy)
        self.assertEqual(proxy.player.make_a_move([]), crazy)
        self.assertEqual(proxy.player.make_a_move([board3, board1a]), crazy)

    def test_query(self):
        self.assertEqual(proxy_remote_player(black, self.name).player.query(["make-a-move"]),crazy)
        self.assertEqual(proxy_remote_player(black, self.name).player.query(["rejister"]), crazy)
        self.assertEqual(proxy_remote_player(black, self.name).player.query(["register"]), "no name")
        self.assertEqual(proxy_remote_player(black, self.name).player.query(["make-a-move", board_history2]), crazy)
        self.assertEqual(proxy_remote_player(black, self.name).player.query(["receive-stones", white]), crazy)
        proxy = proxy_remote_player(black, self.name)
        proxy.player.query(["register"])
        self.assertNotEqual(proxy.player.query(["receive-stones", black]), crazy)
        proxy2 = proxy_remote_player(black, self.name)
        proxy2.player.query(["register"])
        proxy2.player.query(["receive-stones", black])
        self.assertEqual(proxy2.player.query(["make-a-move", board_history1]), "1-3")



if __name__ == "__main__":
    unittest.main()
