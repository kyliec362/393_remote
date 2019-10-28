from backend import backend
import json
import sys
import re
from streamy import stream
import unittest


def populate(input_list):
    list_of_lists = []
    curr_list = []
    list_length = 10
    for i in range(len(input_list)):
        # We've populated the current sub-list with 10 objects,
        # so add to list of filled sub-lists and start fresh
        if i % list_length == 0 and i != 0:
            list_of_lists.append(curr_list)
            curr_list = []
        # Add next element to currently unfilled sub-list
        curr_list.append(input_list[i])
    # Handle last sublist
    if len(curr_list) == list_length:
        list_of_lists.append(curr_list)
    return list_of_lists


def read():
    # Read from std in until no more input is received
    file_contents = ""
    special_json = sys.stdin.readline()
    while special_json:
        file_contents += special_json
        special_json = sys.stdin.readline()
    return file_contents


def sort(list_of_lists):
    # Sort each sub-list using the backend
    for i in range(len(list_of_lists)):
        sorted_list = backend().sort(list_of_lists[i])
        list_of_lists[i] = sorted_list
    return json.dumps(list_of_lists)


def split(file_contents):
    # Decode input into a list of special JSON objects
    lst = list(stream(file_contents))
    # Split list into sub-lists of length 10
    return populate(lst)


class Frontend:
    def __init__(self):
        pass

    def read_split_sort(self):
        print(sort(split(read())))


def main():
    Frontend().read_split_sort()


class FrontendTests(unittest.TestCase):

    def test_split(self):
        test_input = '2\n 4\n6\n 7 5\n"pizza"4\n5\n6\n7\n5"no"\n{"name":"grr"}\n4\n5\n7\n6\n3\n1345346\n234346\n"any more""nope"1'
        test_output = [[2, 4, 6, 7, 5, 'pizza', 4, 5, 6, 7], [5, 'no', {'name': 'grr'}, 4, 5, 7, 6, 3, 1345346, 234346]]
        self.assertEqual(split(test_input), test_output)

    def test_sort(self):
        test_input = [[2, 4, 6, 7, 5, 'pizza', 4, 5, 6, 7], [5, 'no', {'name': 'grr'}, 4, 5, 7, 6, 3, 1345346, 234346]]
        test_output = '[[2, 4, 4, 5, 5, 6, 6, 7, 7, "pizza"], [3, 4, 5, 5, 6, 7, 234346, 1345346, "no", {"name": "grr"}]]'
        self.assertEqual(sort(test_input), test_output)


if __name__ == "__main__":
    main()
    #unittest.main()
