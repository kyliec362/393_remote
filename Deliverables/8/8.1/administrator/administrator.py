import sys
import socket
import json
from player import get_socket_address, proxy_remote_player
from streamy import stream
from board import make_point, board, get_board_length, make_empty_board, parse_point
from referee import referee

# configuration
config_file = open("go.config", "r")
info = list(stream(config_file.readlines()))[0]
default_player_file_path = info["default-player"]
player_pkg = __import__("player_pkg")
from player_pkg import proxy_remote_player
default_player = proxy_remote_player
print(default_player)


maxIntersection = get_board_length()
empty = " "
black = "B"
white = "W"
n = 1
crazy = "GO has gone crazy!"
empty_board = make_empty_board()

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

    def __init__(self):
        self.port = info["port"]
        self.ip = info["IP"]
        self.default_player = default_player(white, "default")
        self.remote_player = None
        self.referee = None

    def check_input(self, input):
        if input == "pass":
            return True
        try:
            parse_point(input)
        except:
            return False
        finally:
            return True

    def setup_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.ip, self.port))
        sock.settimeout(60)
        sock.listen(1)
        return sock

    def referee_two_moves(self, input):
        if self.referee.handle_move(input):
            if self.referee.handle_move(self.default_player.make_a_move(self.referee.board_history)):
                return True
        return False

    def setup_game(self):
        self.remote_player = proxy_remote_player(black, "Yggdrasil")
        self.referee = referee(self.remote_player, self.default_player)
        self.set_true_register_receive_flag(self.default_player)
        self.set_true_register_receive_flag(self.remote_player)


    def set_true_register_receive_flag(self, player):
        player.register_flag = True
        player.receive_flag = True

    def run_server(self):
        sock = self.setup_server()
        output = ""
        client_done_flag = False
        while not client_done_flag:
            connection, client_address = sock.accept()
            try:
                # Receive the data in small chunks and collect it
                while True:
                    data = connection.recv(64)
                    if data:
                        data = data.decode()
                    else:
                        break
                    if data == "done":
                        connection.sendall("done".encode())
                        client_done_flag = True
                        break
                    elif data == "WITNESS ME":
                        self.setup_game()
                        connection.sendall(json.dumps(self.referee.board_history).encode())
                        break
                    else:
                        if self.check_input(data):
                            if self.referee_two_moves(data):
                                connection.sendall(json.dumps(self.referee.board_history).encode())
                                continue
                        output = self.referee.get_winner()
                        client_done_flag = True
                        break

            finally:
                # Clean up the connection
                connection.close()
        # done shouldn't be part of the game-play output, it is just a client-server acknowledgement
        output = list(stream(output))
        print(json.dumps(output))



if __name__ == '__main__':
    admin = administrator()
    admin.run_server()
