import sys
import socket
import json
from streamy import stream
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
    lst = read_input_from_file()
    #lst = [["register"], ["receive-stones", "B"] ,["receive-stones", "W"] , ["receive-stones", "B"] ,["receive-stones", "W"]]
    # create server (simulate referee)
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 8002)
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
                    output = ""
                    break
                else:
                    obj_from_client -= 1
                    break
        finally:
            # Clean up the connection
            connection.close()
    print(json.dumps(list(stream(output))))


if __name__ == "__main__":
    main()
