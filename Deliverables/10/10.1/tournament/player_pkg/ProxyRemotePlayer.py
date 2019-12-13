from .Player import Player
import sys
import json
sys.path.append('../')
from const import *
from utils import *


class proxy_remote_player(Player):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        # give 30 seconds for remote players or assume disconnect
        self.connection.settimeout(30)

    def make_a_move(self, boards):
        try:
            move_msg = '["make-a-move",' + json.dumps(boards) + ']'
            self.connection.sendall(move_msg.encode())
        except Exception as e:
            print("Make a move send -> Exception is %s" % e)
            self.connection.close()
            return
        try:
            data = self.connection.recv(recv_size_player)
            if data:
                print(26, data)
                return json.loads(data.decode())
        except Exception as e:
            print("Make a move failed receiving. Exception is %s" % e)
            self.connection.close()

    def register(self):
        try:
            self.connection.sendall('["register"]'.encode())
            data = self.connection.recv(recv_size_player)
            if data:
                self.name = json.loads(data.decode())
                # if self.name == crazy:
                #     self.connection.close()
                # else:
                self.register_flag = True
        except Exception as e:
            print("Register failed sending. Exception is %s" % e)
            self.connection.close()
        return self.name

    def receive_stones(self, stone):
        try:
            recv_msg = '["receive-stones",' + '"' + stone + '"' + ']'
            self.connection.sendall(recv_msg.encode())
        except Exception as e:
            print("Receive failed sending. Exception is %s" % e)
            self.connection.close()
        else:
            self.receive_flag = True
            self.stone = stone

    def end_game(self):
        try:
            self.connection.sendall('["end-game"]'.encode())
            response = self.connection.recv(recv_size_player)
            # print("proxy end game 66", response)
            if response:
                response = json.loads(response.decode())
                if response == "OK":
                    return response
        except Exception as e:
            print("End game failed sending. Exception is %s" % e)
            self.connection.close()
