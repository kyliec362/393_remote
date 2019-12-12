from .Player import Player
import sys
import json
sys.path.append('../')
from const import *
from utils import *


class proxy_remote_player(Player):
    def __init__(self, connection, name=random_string()):
        super().__init__(name)
        self.connection = connection
        # give 30 seconds for remote players or assume disconnect
        self.connection.settimeout(30)

    def make_a_move(self, boards):
        try:
            move_msg = '["make-a-move",' + json.dumps(boards) + ']'
            self.connection.sendall(move_msg.encode())
        except Exception as e:
            print("Make a move send -> Exception is %s" % e)
            return False
        try:
            data = self.connection.recv(recv_size_player)
            # print("proxy 31", data)
            if data:
                return data.decode()
            return False
        except Exception as e:
            print("Make a move failed receiving. Exception is %s" % e)
            return False

    def register(self):
        try:
            self.connection.sendall('["register"]'.encode())
            data = self.connection.recv(recv_size_player)
            if data:
                self.name = data.decode()
                if self.name == crazy:
                    print("crazy register proxy")
                    return False
                self.register_flag = True
                return True
        except Exception as e:
            print("Register failed sending. Exception is %s" % e)
            return False
        print("Register failed without an exception")
        return False

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
