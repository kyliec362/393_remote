from .Player import Player
import sys
import json
import socket
import time
sys.path.append('../')
from streamy import stream
from const import *
from utils import *


class proxy_remote_player(Player):
    def __init__(self, connection, name=random_string()):
        print("proxy @ 14")
        super().__init__(name)
        self.connection = connection

    def make_a_move(self, boards):
        print("proxy 17", self.connection)
        try:
            move_msg = '["make-a-move",' + json.dumps(boards) + ']'
            print("proxy 20", self.connection)
            self.connection.sendall(move_msg.encode())
            print("proxy 22", self.connection)
        except Exception as e:
            print("Make a move send -> Exception is %s" % e)
            return False
        try:
            print("proxy 29")
            data = self.connection.recv(recv_size_player)
            print("proxy 31", data)
            if data:
                return data.decode()
            return False
        except Exception as e:
            print("Make a move failed receiving. Exception is %s" % e)
            return False

    def register(self):
        # print("proxy @ 33")
        try:
            self.connection.sendall('["register"]'.encode())
            # TODO make sure we don't get crazy msg returned
            # print("proxy @ 37", self.connection)
            data = self.connection.recv(recv_size_player)
            # print("proxy @ 39", data, self.connection)
            if data:
                self.name = data.decode()
                self.register_flag = True
                return True
        except Exception as e:
            print("Register failed sending. Exception is %s" % e)
            return False
        print("Register failed without an exception")
        return False

    def receive_stones(self, stone):
        try:
            print("proxy @ 50")
            recv_msg = '["receive-stones",' + '"' + stone + '"' + ']'
            self.connection.sendall(recv_msg.encode())
        except Exception as e:
            print("Receive failed sending. Exception is %s" % e)
            return False
        else:
            print("proxy @ 57")
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
