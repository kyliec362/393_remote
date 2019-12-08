from .Player import Player
import sys
import json
import socket
sys.path.append('../')
from streamy import stream
from const import *


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
            print(67, data.decode())
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
