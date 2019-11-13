import sys
import socket
import json
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



def main():
    """
    Test Driver reads json objects from stdin
    Uses the streamy library to parse
    Queries player
    :return: list of json objects
    """
    # create server (simulate referee)
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = get_socket_address()
    sock.bind(server_address)
    sock.settimeout(60)
    sock.listen(1)
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
                    output += data
                else:
                    break
                if data == "done":
                    connection.sendall("done".encode())
                    client_done_flag = True
                    break
                if data == "WITNESS ME":
                    lst = read_input_from_file()
                    connection.sendall(json.dumps(lst).encode())
                    output = ""
                    break
        finally:
            # Clean up the connection
            connection.close()
    # done shouldn't be part of the game-play output, it is just a client-server acknowledgement
    output = output.replace("done", "")
    output = list(stream(output))
    output = output[0]
    print(json.dumps(output))


if __name__ == "__main__":
    main()
