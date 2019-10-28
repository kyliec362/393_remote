import json
import functools
import sys
from streamy import stream
import unittest

'''
Backend
Takes in 10 json objects
Returns sorted list of the json objects
'''

# associate numbers with different types that reflect type precedence for sorting
# constant dictionary
types = {'int': 0, 'float': 0, 'str': 1, 'dict': 2}


def compare_helper(a, b):
    """
    A helper function to compare two objects of the same type.

    Args:
        a and b are either both strings or both numbers
    Returns:
        True if a is greater, false if a is less, 0 otherwise
    """
    if a > b:
        return 1
    elif a < b:
        return -1
    else:
        return 0


def compare(a, b):
    """
    A comparator method to compare two json objects

    Args:
        a and b are both json objects (string, number, dict)
    Returns:
        True if a is greater, false if a is less, 0 otherwise
    """
    # interface checking
    if type(a).__name__ not in types or type(b).__name__ not in types:
        raise Exception("Invalid JSON object type")
    a_type = types[type(a).__name__]
    b_type = types[type(b).__name__]
    # associate numbers with different types that reflect type precedence for sorting
    diff = a_type - b_type
    # if types of two inputs are the same
    if diff == 0:
        if a_type < 2:
            diff = compare_helper(a, b)
        else:
            # need to recurse to see if a json obj contains another json obj
            diff = compare(a['name'], b['name'])
    return diff  # return the type precedence difference


class backend:
    def __init__(self):
        pass

    def sort(self, json_list):
        """
        Method that
        :param json_list: list of json objects
        :return: list of json objects (sorted)
        """
        if len(json_list) != 10:  # interface check
            raise Exception("Sort function expects 10 json objects")
        return sorted(json_list, key=functools.cmp_to_key(compare))


def main():
    """
    Test Driver reads 10 json objects from stdin
    Uses the streamy library to parse
    Returns sorted list to stdout
    :return: list of json objects
    """
    file_contents = ""  # read in all 10 json objects to a string
    special_json = sys.stdin.readline()
    while special_json:
        file_contents += special_json
        special_json = sys.stdin.readline()
    lst = list(stream(file_contents))  # parse json objects
    lst = backend().sort(lst)
    print(json.dumps(lst))


class BackendTests(unittest.TestCase):

    def test_sort(self):
        b = backend()
        s = [3, 6, "hi", 8, "wow", {"name": {"name": 3}}, 0, 1000, 1, "my"]
        self.assertEqual(b.sort(s), [0, 1, 3, 6, 8, 1000, "hi", "my", "wow", {"name": {"name": 3}}])

    def test_interface(self):
        # check that sort fails when less than 10 objects
        b = backend()
        with self.assertRaises(Exception):
            b.sort([1, "hi", 9])

    def test_nestedJson(self):
        b = backend()
        s = [{"name": {"name": 9}}, 2, 4, 5, 3, "more", {"name": {"name": "this"}}, 9, 1000, 3]
        self.assertEqual(b.sort(s), [2, 3, 3, 4, 5, 9, 1000, "more", {"name": {"name": 9}}, {"name": {"name": "this"}}])


if __name__ == "__main__":
    main()
    # unittest.main()
