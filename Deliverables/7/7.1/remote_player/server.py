import sys
import socket
import json
import subprocess
from streamy import stream
from player import get_socket_address
from rule_checker import rule_checker, get_opponent_stone
from board import make_point, board, get_board_length

maxIntersection = get_board_length()
empty = " "
black = "B"
white = "W"
n = 1
crazy = "GO has gone crazy!"

def read_input_from_file():
    file_contents = ""  # read in all json objects to a string
    special_json = sys.stdin.readline()
    while special_json:
        file_contents += special_json
        special_json = sys.stdin.readline()
    return list(stream(file_contents))  # parse json objects



def main():
    """
    Test Driver reads json objects from stdin
    Uses the streamy library to parse
    Queries player
    :return: list of json objects
    """
    print("running server main")
    lst = read_input_from_file()
    file_contents = ""  # read in all json objects to a string
    special_json = sys.stdin.readline()
    while special_json:
        file_contents += special_json
        special_json = sys.stdin.readline()

    lst = list(stream(file_contents))  # parse json objects
    print(lst)
    #lst = [["register"], ["receive-stones", "B"], ["receive-stones", "W"], ["receive-stones", "B"], ["receive-stones", "W"]]
    # create server (simulate referee)
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = get_socket_address()
    sock.bind(server_address)
    sock.listen(1)
    output = ""
    obj_from_client = 2
    while obj_from_client > 0:
        connection, client_address = sock.accept()
        try:
            # Receive the data in small chunks and collect it
            while True:
                data = connection.recv(16)
                if data:
                    output += data.decode()
                if output == "WITNESS ME":
                    connection.sendall(json.dumps(lst).encode())
                    obj_from_client -= 1
                    #output = ""
                    break
                else:
                    obj_from_client -= 1
                    break
        finally:
            # Clean up the connection
            print("closing connection in server")
            print("ouput 74 in player", output)
            #print("server output", json.dumps(list(stream(output))))
            connection.close()



if __name__ == "__main__":
    main()
