import sys
import socket
import json
import random
sys.path.append('../')
from streamy import stream
from rule_checker import rule_checker, get_opponent_stone
from board import make_point, board, get_board_length
import time

maxIntersection = get_board_length()
empty = " "
black = "B"
white = "W"
n = 1
recv_size = 8192  # amount we can receive at a time (pseudo arbitrary)

crazy = "GO has gone crazy!"
history = "This history makes no sense!"

# read 'capture in n moves' depth from config file
def set_depth():
    pass
    # config_file = open("go-player.config", "r")
    # depth = config_file.readlines()
    # depth_info = list(stream(depth))[0]
    # print(depth_info)
    # global n
    # n = depth_info["depth"]


def get_socket_address():
    # return ("localhost", 8080)
    config_file = open("go.config", "r")
    socket_info = config_file.readlines()
    socket_info = list(stream(socket_info))[0]
    port = socket_info["port"]
    ip = socket_info["IP"]
    return (ip, port)

def client(message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = get_socket_address()
    sock.settimeout(5)
    sock.connect(server_address)
    response = ""
    try:
        sock.sendall(message.encode())
        print("sent to tournament " + message)
        while True:
            received = sock.recv(recv_size)
            print(51, received)
            if received:
                response += received.decode()
            else:
                break
    except:
        sock.close()
        return response
    finally:
        sock.close()
    return response


def generate_random_point():
    return make_point(random.randint(0, maxIntersection - 1), random.randint(0, maxIntersection - 1))

class player:

    function_names = ['register', 'receive_stones', 'make_a_move']

    def __init__(self, stone, name):
        self.stone = stone
        self.name = name
        self.register_flag = False
        self.receive_flag = False
        self.crazy_flag = False

    def query(self, query_lst):
        # don't keep playing if we've gone crazy (deviated from following rules)
        if self.crazy_flag:
            return
        # get method and arguments from input query
        try:
            method = query_lst[0].replace("-", "_")
            args = query_lst[1:]
            if method not in self.function_names:
                return self.go_crazy()
            method = getattr(self, method)
            if method:
                return method(*args)
            return self.go_crazy()
        except:
            return self.go_crazy()

    def register(self):
        if self.receive_flag or self.register_flag:
            return self.go_crazy()
        self.register_flag = True
        return "no name"

    def receive_stones(self, stone):
        #if not self.is_stone(stone):
        #    return self.go_crazy()
        #if self.receive_flag or not self.register_flag:
        #    return self.go_crazy()
        self.receive_flag = True
        self.stone = stone
        #return True

    def end_game(self):
        self.receive_flag = False
        return "OK"

    def is_stone(self, stone):
        if stone == black or stone == white:
            return True
        return False

    def is_maybe_stone(self, maybe_stone):
        if self.is_stone(maybe_stone) or maybe_stone == empty:
            return True
        return False

    def check_boards_object(self, boards):
        min_boards_size = 1
        max_boards_size = 3
        # check to make sure input is actually a list
        if not isinstance(boards, list):
            return False
        # board history between length 1 and 3
        if len(boards) < min_boards_size or len(boards) > max_boards_size:
            return False
        for board in boards:
            if not self.check_board_object(board):
                return False
        return True

    def check_board_object(self, board):
        # check types
        if not isinstance(board, list):
            print("check board @ 142")
            return False
        if not isinstance(board[0], list):
            print("check board @ 145")
            return False
        # check dimensions
        if len(board) != maxIntersection or len(board[0]) != maxIntersection:
            print("check board @ 149")
            return False
        # make sure all boards contain only maybe stones
        for i in range(maxIntersection):
            for j in range(maxIntersection):
                if not self.is_maybe_stone(board[i][j]):
                    print("check board @ 155")
                    return False
        return True

    def go_crazy(self):
        self.crazy_flag = True
        return crazy

    def make_a_move_random(self, boards):
        # don't make a move until a player has been registered with a given stone
        if self.receive_flag and self.register_flag:
            if rule_checker().check_history(boards, self.stone):
                generate_random_point()
                point = generate_random_point()
                if rule_checker().check_validity(self.stone, [point, boards]):
                    return point
                return "pass"
            return history
        return self.go_crazy()

    def make_a_move_random_maybe_illegal(self, boards):
        # don't make a move until a player has been registered with a given stone
        if self.receive_flag and self.register_flag:
            if rule_checker().check_history(boards, self.stone):
                point = generate_random_point()
                if random.randint(0, maxIntersection - 1) % 3 != 0:
                    return point
                return "pass"
            return history
        return self.go_crazy()

    def make_a_move_dumb(self, boards):
        # don't make a move until a player has been registered with a given stone
        if self.receive_flag and self.register_flag:
            if rule_checker().check_history(boards, self.stone):
                curr_board = boards[0]
                # go through rows and columns to find a point
                # check_validity of that move
                for i in range(maxIntersection):  # row
                    for j in range(maxIntersection):  # col
                        if curr_board[j][i] == empty:
                            point = make_point(i, j)
                            if rule_checker().check_validity(self.stone, [point, boards]):
                                return point
                return "pass"
            return history
        return self.go_crazy()

    def make_a_move(self, boards):
        print("Player make_a_move @ 199")
        # m = self.make_a_move_random_maybe_illegal(boards)
        # return m
        # don't make a move until a player has been registered with a given stone
        if self.receive_flag and self.register_flag:
            if self.check_boards_object(boards):
                if rule_checker().check_history(boards, self.stone):
                    curr_board = boards[0]
                    non_capture_move = None
                    # go through rows and columns to find a point
                    # check_validity of that move
                    for i in range(maxIntersection):  # row
                        for j in range(maxIntersection):  # col
                            point = make_point(i, j)
                            if curr_board[j][i] == empty:
                                if rule_checker().check_validity(self.stone, [point, boards]):
                                    if self.make_capture_n_moves(n, curr_board, self.stone, point, boards):
                                        return point
                                    elif non_capture_move is None:
                                        non_capture_move = point
                    if non_capture_move:
                        return non_capture_move
                    return "pass"
                return history
            print("crazy @ 224")
            return self.go_crazy()
        print("crazy @ 226")
        return self.go_crazy()

    def make_capture_n_moves(self, n, curr_board, stone, point, boards):
        if n == 1:
            return self.make_capture_1_move(curr_board, stone, point)
        new_boards = self.randomize_next_move(n, curr_board, stone, point, boards)
        updated_board = new_boards[0]
        for i in range(maxIntersection):
            for j in range(maxIntersection):
                new_point = make_point(i, j)
                if updated_board[j][i] == empty and rule_checker().check_validity(stone, [new_point, new_boards]):
                    if self.make_capture_1_move(updated_board, stone, new_point):
                        return True
        return False

    def randomize_next_move(self, n, curr_board, stone, point, boards):
        if n == 1:
            return boards
        curr_board = board(curr_board)
        updated_board = curr_board.place(stone, point)
        new_boards = [updated_board] + boards[:min(2, len(boards))]
        opponent_random_move = self.next_player_move(stone, new_boards)
        if opponent_random_move == "pass":
            new_boards = [new_boards[0]] + [new_boards[0]] + [new_boards[1]]
        else:
            new_boards = [board(new_boards[0]).place(get_opponent_stone(stone), opponent_random_move)] + \
                         [new_boards[0]] + [new_boards[1]]
        point = self.make_a_move_dumb(new_boards)
        return self.randomize_next_move(n - 1, new_boards[0], stone, point, new_boards)

    def next_player_move(self, stone, new_boards):
        next_player = player(get_opponent_stone(stone))
        next_player.register_flag = True
        next_player.receive_flag = True
        return next_player.make_a_move_dumb(new_boards)

    def make_capture_1_move(self, curr_board, stone, point):
        curr_board = board(curr_board)
        updated_board = curr_board.place(stone, point)
        stones_to_remove = board(updated_board).get_no_liberties(get_opponent_stone(stone))
        if len(stones_to_remove) > 0:
            return True
        return False


class proxy_remote_player:
    def __init__(self, connection, stone, name):
        # self.player = player(stone, name)
        self.connection = connection
        self.name = name
        self.stone = stone
        self.register_flag = False
        self.receive_flag = False

    def make_a_move(self, boards):
        print(277)
        try:
            #time.sleep(1)
            move_msg = '["make-a-move",' + json.dumps(boards) + ']'
            print(279, move_msg)
            print(281, self.connection)
            print("284 connection in player_file make_a_move before connection.send", self.connection)
            self.connection.sendall(move_msg.encode())
            print("286 connection in player_file make_a_move after connection.send", self.connection)
        except Exception as e:
            print("Make a move send -> Exception is %s" % e)
            return False
        try:
            print(287)
            print("connection in player_file make_a_move before data.recv", self.connection)
            data = self.connection.recv(recv_size)
            print("connection in player_file make_a_move after data.recv", self.connection)
            print("player_file.py data: ", data)
            if data:
                print("player_file,py data: ", data.decode())
                return data.decode()
            return False
        except Exception as e:
            print("Make a move failed receiving. Exception is %s" % e)
            return False

    def register(self):
        try:
            self.connection.sendall('["register"]'.encode())
            # TODO make sure we don't get crazy msg returned
            data = self.connection.recv(recv_size)
            print("303 and recv data that should be player object in register in proxy ", data)
            if data:
                self.register_flag = True
                return True
        except Exception as e:
            print("Register failed sending. Exception is %s" % e)
            return False
        #print(308, "register no exception but no responses")
        return True #False

    def receive_stones(self, stone):
        try:
            print(307)
            recv_msg = '["receive-stones",' + '"' + stone + '"' + ']'
            print("player_File before sending recv_msg", recv_msg)
            print("recv_msg.encode", recv_msg.encode())
            self.connection.sendall(recv_msg.encode())
        except Exception as e:
            print("Receive failed sending. Exception is %s" % e)
            return False
        else:
            self.receive_flag = True
            self.stone = stone
            return True

    def end_game(self):
        response = ""
        try:
            self.connection.sendall('["end-game"]'.encode())
            while True:
                received = self.connection.recv(recv_size)
                if received:
                    response += received.decode()
                else:
                    break
        except Exception as e:
            print("End game failed sending. Exception is %s" % e)
            return False
        else:
            if response == "OK":
                return response
            return False

def main():
    set_depth()



if __name__ == "__main__":
    main()