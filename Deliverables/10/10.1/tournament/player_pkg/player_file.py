import sys
import socket
import abc
import json
import random
# from matplotlib import pyplot as plt
# from matplotlib.widgets import TextBox
sys.path.append('../')
from streamy import stream
from rule_checker import rule_checker, get_opponent_stone, get_legal_moves
from board import make_point, board, get_board_length, make_empty_board, parse_point
from const import *
from referee import update_board_history

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
        while True:
            received = sock.recv(recv_size_player)
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

class Player(abc.ABC):
    function_names = ['register', 'receive_stones', 'make_a_move']

    def __init__(self, stone, name):
        self.stone = stone
        self.name = name
        self.register_flag = False
        self.receive_flag = False
        self.crazy_flag = False

    @abc.abstractmethod
    def make_a_move(self, boards):
        pass

    @abc.abstractmethod
    def register(self):
        pass

    @abc.abstractmethod
    def receive_stones(self, stone):
        pass


class player(Player):

    function_names = ['register', 'receive_stones', 'make_a_move']

    def __init__(self, stone, name):
        super().__init__(stone, name)
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
        return no_name

    def receive_stones(self, stone):
        #if not self.is_stone(stone):
        #    return self.go_crazy()
        #if self.receive_flag or not self.register_flag:
        #    return self.go_crazy()
        self.receive_flag = True
        self.stone = stone

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
            return False
        if not isinstance(board[0], list):
            return False
        # check dimensions
        if len(board) != maxIntersection or len(board[0]) != maxIntersection:
            return False
        # make sure all boards contain only maybe stones
        for i in range(maxIntersection):
            for j in range(maxIntersection):
                if not self.is_maybe_stone(board[i][j]):
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

    def make_a_move_end_game_quickly(self, boards):
        r = random.randint(0, 10)
        if r == 0:
            return generate_random_point()
        if r == 1:
            return self.go_crazy()
        if r == 2:
            return history
        if r >= 3:
            return "pass"


    def make_a_move(self, boards):
        m = self.make_a_move_end_game_quickly(boards)
        return m
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


class proxy_remote_player(Player):
    def __init__(self, connection, stone, name):
        super().__init__(stone, name)
        self.connection = connection

    def make_a_move(self, boards):
        try:
            move_msg = '["make-a-move",' + json.dumps(boards) + ']'
            self.connection.sendall(move_msg.encode())
        except Exception as e:
            print("Make a move send -> Exception is %s" % e)
            return False
        try:
            data = self.connection.recv(recv_size_player)
            if data:
                return data.decode()
            return False
        except Exception as e:
            print("Make a move failed receiving. Exception is %s" % e)
            return False

    def register(self):
        try:
            self.connection.sendall('["register"]'.encode())
            # TODO make sure we don't get crazy msg returned
            data = self.connection.recv(recv_size_player)
            if data:
                self.register_flag = True
                return True
        except Exception as e:
            print("Register failed sending. Exception is %s" % e)
            return False
        return True #False

    def receive_stones(self, stone):
        try:
            recv_msg = '["receive-stones",' + '"' + stone + '"' + ']'
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
            response = self.connection.recv(recv_size_player)
            if response:
                return True
        except Exception as e:
            print("End game failed sending. Exception is %s" % e)
            return False
        else:
            if response == "OK":
                return response
        return False

class AlphaBetaPlayer(Player):
    def __init__(self, stone, name, depth):
        self.depth = depth
        super().__init__(stone, name)

    def register(self):
        if self.receive_flag or self.register_flag:
            return self.go_crazy()
        self.register_flag = True
        return "no name"

    def receive_stones(self, stone):
        self.receive_flag = True
        self.stone = stone

    def go_crazy(self):
        self.crazy_flag = True
        return crazy

    def end_game(self):
        self.receive_flag = False
        return "OK"

    def make_a_move(self, boards):
        return (self.ab_minimax(0, self.depth, True, NEG_INF, POS_INF, boards))[1]

    def heuristic(self, curr_board):
        return board(curr_board).calculate_score()[self.stone]

    def ab_minimax(self, depth, max_depth, is_maximizer, alpha, beta, boards):
        curr_board = boards[0]
        if is_maximizer:
            legal_moves = get_legal_moves(boards, self.stone)
        else:
            legal_moves = get_legal_moves(boards, get_opponent_stone(self.stone))

        if (depth == max_depth) or (len(legal_moves) == 0):
            return [self.heuristic(curr_board), "hello"]  # heuristic for game evaluation
        updated_board = curr_board
        if is_maximizer:
            max_eval = [alpha, None]
            for move in legal_moves:
                if move != "pass":
                    updated_board = board(curr_board).place(self.stone, move)
                updated_history = update_board_history(updated_board, boards)
                result = self.ab_minimax(depth + 1, max_depth, not is_maximizer, alpha, beta, updated_history)
                result[1] = move
                max_eval = max(max_eval, result, key=lambda x: x[0])
                alpha = max(alpha, result[0])
                if beta <= alpha:
                    break
            return max_eval

        else:
            min_eval = [beta, None]
            for move in legal_moves:
                if move != "pass":
                    updated_board = board(curr_board).place(self.stone, move)
                updated_history = update_board_history(updated_board, boards)
                result = self.ab_minimax(depth + 1, max_depth, not is_maximizer, alpha, beta, updated_history)
                result[1] = move
                min_eval = min(min_eval, result, key=lambda x: x[0])
                beta = min(beta, result[0])
                if beta <= alpha:
                    break
            return min_eval

# class GuiPlayer(Player):
#     def __init__(self, stone, name):
#         name = ""
#         self.name_from_user()
#         super().__init__(stone, name)
#         self.register_flag = False
#         self.receive_flag = False
#         self.crazy_flag = False
#         self.next_move = None
#         self.next_move_flag = False
#
#     def go_crazy(self):
#         self.crazy_flag = True
#         return crazy
#
#
#     def register(self):
#         if self.receive_flag or self.register_flag:
#             return self.go_crazy()
#         self.register_flag = True
#         return no_name
#
#     def receive_stones(self, stone):
#         self.receive_flag = True
#         self.stone = stone
#
#     def end_game(self):
#         self.receive_flag = False
#         return "OK"
#
#     def name_from_user(self):
#         def submit(text):
#             plt.close()
#             self.name = text
#
#         axbox = plt.axes([0.1, 0.05, 0.8, 0.075])
#         text_box = TextBox(axbox, 'Name: ', initial="")
#         text_box.on_submit(submit)
#         plt.show()
#
#     def display(self, curr_board):
#         # create a 8" x 8" board
#         fig = plt.figure(figsize=[8, 8])
#         fig.patch.set_facecolor((1, 1, .8))
#         ax = fig.add_subplot(111)
#
#         #fig.suptitle(self.player1.name + " (black)" + " vs. " + self.player2.name + " (white)", fontsize=16)
#
#         # draw the grid
#         for x in range(maxIntersection):
#             ax.plot([x, x], [0, maxIntersection - 1], 'k')
#         for y in range(maxIntersection):
#             ax.plot([0, maxIntersection - 1], [y, y], 'k')
#
#         # scale the axis area to fill the whole figure
#         ax.set_position([0, 0, 1, 1])
#
#         # get rid of axes and everything (the figure background will show through)
#         ax.set_axis_off()
#
#         # scale the plot area conveniently (the board is in 0,0..18,18)
#         ax.set_xlim(-1, maxIntersection)
#         ax.set_ylim(-1, maxIntersection)
#
#         fig.canvas.mpl_connect('button_press_event', self.onclick)
#
#         # draw Go stones at (10,10) and (13,16)
#         for p in curr_board.get_points(black):
#             xy = parse_point(p)
#             ax.plot(xy[1], maxIntersection - 1 - xy[0], 'o', markersize=25, markeredgecolor=(.5, .5, .5),
#                     markerfacecolor='k', markeredgewidth=2)
#         for p in curr_board.get_points(white):
#             xy = parse_point(p)
#             ax.plot(xy[1], maxIntersection - 1 - xy[0], 'o', markersize=25, markeredgecolor=(0, 0, 0),
#                     markerfacecolor='w', markeredgewidth=2)
#
#         plt.show()
#
#     def point_from_click_data(self, xdata, ydata):
#         x = int(round(xdata))
#         y = maxIntersection - 1 - int(round(ydata))
#         return x, y
#
#     def onclick(self, event):
#         plt.close()
#         x, y = self.point_from_click_data(event.xdata, event.ydata)
#         self.next_move = make_point(x, y)
#         self.next_move_flag = True
#
#     def make_a_move(self, boards):
#         self.display(board(boards[0]))
#         if self.next_move_flag:
#             self.next_move_flag = False
#             return self.next_move
#         return "pass"
#






def main():
    set_depth()
    print(GuiPlayer(black).make_a_move(board_history1))



if __name__ == "__main__":
    main()