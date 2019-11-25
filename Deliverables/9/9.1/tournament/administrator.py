import sys
import json
from .streamy import stream
from .board import get_board_length, make_empty_board, parse_point
from .referee import referee

# configuration
config_file = open("go.config", "r")
info = list(stream(config_file.readlines()))[0]
default_player_file_path = info["default-player"]
#player_pkg = __import__(default_player_file_path)
from .player_pkg import proxy_remote_player, player

default_player = player

maxIntersection = get_board_length()
empty = " "
black = "B"
white = "W"
n = 1
crazy = "GO has gone crazy!"
history = "This history makes no sense!"
empty_board = make_empty_board()
recv_size = 64


def read_input_from_file():
    file_contents = ""  # read in all json objects to a string
    file_contents_so_far = ""
    special_json = sys.stdin.readline()
    while special_json:
        file_contents += special_json
        special_json = sys.stdin.readline()
        decoded = ""
        # try to decode into json as we go
        # because if something later breaks the json formatting
        # we still want to be able to run all prior valid json
        try:
            decoded = list(stream(file_contents))
        except:
            continue
        if len(decoded) > 0:
            file_contents_so_far = list(stream(file_contents))
    try:
        return list(stream(file_contents))  # parse json objects
    except:
        if len(file_contents_so_far) > 0:
            return file_contents_so_far
        return [crazy]


class administrator:

    def __init__(self, player1, player2, conn1, conn2):
        self.player2 = player2
        self.player1 = player1
        self.conn2 = conn2
        self.conn1 = conn1
        self.referee = None
        self.client_done_flag = False

    def opposite_wins(self):
        return [json.dumps(self.referee.get_opposite_player().name)]

    def check_input(self, input):
        if input == "pass":
            return True
        if input == crazy or input == history:
            return False
        try:
            parse_point(input)
        except:
            return False
        finally:
            return True

    # TODO add a while loop method that referees all moves until games over

    def referee_move(self, input):
        if self.referee.handle_move(input):
            return True
        return False

    def setup_game(self):
        self.player1 = player(black, "Yggdrasil")
        self.referee = referee(self.player1, self.player2)
        self.set_true_register_receive_flag(self.player2)
        self.set_true_register_receive_flag(self.player1)

    def set_client_done_flag(self):
        self.client_done_flag = not self.client_done_flag

    def set_true_register_receive_flag(self, player):
        player.register_flag = True
        player.receive_flag = True

    # TODO When a game finishes your referee should notify both players in a game that the game is over.
    # For remote players this boils down to receiving a message ["end-game"]
    # to which it replies with the JSON string "OK".
    def send_end_game_message(self):
        self.conn1.sendall(json.dumps('["end-game]').encode())
        self.conn2.sendall(json.dumps('["end-game]').encode())

    def run_game(self):
        self.setup_game()

        while True:
            if self.referee.current_player == self.player1:
                game_output = self.connection_helper(self.conn1)
            else:
                game_output = self.connection_helper(self.conn2)

            if game_output:
                self.send_end_game_message()
                return game_output

    def connection_helper(self, connection):
        try:
            data = self.connection.recv(recv_size)
            if data:
                data = data.decode()
            else:
                # TODO not sure if correct
                return
            if data == "WITNESS ME":
                self.connection.sendall(json.dumps(self.referee.board_history).encode())
            else:
                if self.check_input(data):
                    if self.referee_move(data):
                        connection.sendall(json.dumps(self.referee.board_history).encode())

                    else:
                        connection.close()
                        return self.referee.get_winner()
                else:
                    connection.close()
                    return self.opposite_wins()
        # TODO ? client disconnects? (*chuckles* I'm in danger)
        except:
            return self.opposite_wins()




if __name__ == '__main__':
    pass

