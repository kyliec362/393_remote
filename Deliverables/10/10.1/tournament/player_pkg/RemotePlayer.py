import socket
import sys
sys.path.append('../')
from streamy import stream
from const import *
from player_pkg import player, GuiPlayer
default_player = GuiPlayer

def query(p, query_lst):
    print("remote @ 10", query_lst)
    # don't keep playing if we've gone crazy (deviated from following rules)
    if p.crazy_flag:
        return
    # get method and arguments from input query
    try:
        method = query_lst[0].replace("-", "_")
        args = query_lst[1:]
        print("17 @ remote player", method, args)
        if method not in p.function_names:
            return p.go_crazy()
        method = getattr(p, method)
        if method:
            return method(*args)
        return p.go_crazy()
    except:
        return p.go_crazy()

def get_socket_address():
    config_file = open("../go.config", "r")
    socket_info = config_file.readlines()
    socket_info = list(stream(socket_info))[0]
    port = socket_info["port"]
    ip = socket_info["IP"]
    return (ip, port)


def get_connection_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = get_socket_address()
    sock.settimeout(30)
    sock.connect(server_address)
    return sock

def client_recv(sock):
    response = ""
    try:
        while True:
            received = sock.recv(recv_size_player)
            print("client @ 47", received)
            if received:
                response += received.decode()
            break
    except:
        pass
    return response


def client(sock, message):
    # print("remote 57", sock)
    response = ""
    print("client @ 59", message, sock)
    try:
        if message is not None:
            sock.sendall(message.encode())
            while True:
                received = sock.recv(recv_size_player)
                # print("client @ 65", received)
                if received:
                    response += received.decode()
                break
    except Exception as e:
        print("Client exception in remote player. Exception is %s" % e)
        return -1
    return response


def main():
    sock = get_connection_socket()
    end_game_flag = False
    proxy = default_player()
    server_response = client(sock, "WITNESS ME")
    while not end_game_flag and server_response != -1:
        if len(server_response) < 1:
            server_response = client_recv(sock)
        try:
            qry = list(stream(server_response))[0]  # parse json objects
        except:
            proxy.go_crazy()
            server_response = client(sock, crazy)
        else:
            if "end" in qry[0]:
                end_game_flag = True
            result = query(proxy, qry)
            server_response = client(sock, result)
    sock.close()
    return


if __name__ == "__main__":
    main()
