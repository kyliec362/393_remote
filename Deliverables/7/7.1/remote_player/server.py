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
    special_json = sys.stdin.readline()
    while special_json:
        file_contents += special_json
        special_json = sys.stdin.readline()
    return file_contents
    #return list(stream(file_contents))  # parse json objects



def main():
    """
    Test Driver reads json objects from stdin
    Uses the streamy library to parse
    Queries player
    :return: list of json objects
    """
    # print("running server main")
    #lst = [["register"], ["receive-stones", "B"], ["receive-stones", "W"], ["receive-stones", "B"], ["receive-stones", "W"]]
    # create server (simulate referee)
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = get_socket_address()
    sock.bind(server_address)
    sock.settimeout(60)
    # print(server_address)
    sock.listen(1)
    output = ""
    client_done_flag = False
    # print(44)
    while not client_done_flag:
        connection, client_address = sock.accept()
        # print(47)
        try:
            # Receive the data in small chunks and collect it
            while True:
                data = connection.recv(64)
                # print(59,data)
                if data:
                    data = data.decode()
                    # print(61,data)
                    output += data
                else:
                    # print(65)
                    break
                if data == "done":
                    # print("done flag set")
                    connection.sendall("done".encode())
                    client_done_flag = True
                    break
                if data == "WITNESS ME":
                    # print(64)
                    file_contents = read_input_from_file()
                    # print(lst)
                    connection.sendall(file_contents.encode())
                    output = ""
                    break
        finally:
            # Clean up the connection
            # print("closing connection in server")
            connection.close()
    # print(73, output)
    output = output.replace("done","")
    output = list(stream(output))
    output = output[0]
    print(json.dumps(output))


if __name__ == "__main__":
    main()
