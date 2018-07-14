import unittest
import tempfile
import os.path


def read(result, minisat=False):
    if minisat:
        return read_minisat(result)

    s = None
    values = []
    with open(result, "rt", encoding="utf8") as output:
        for line in output:
            if line.startswith("s S"):
                s = True
            if line.startswith("s U"):
                s = False
            elif line.startswith("v "):
                values += map(int, line.split()[1:])
    while len(values) > 0 and values[-1] == 0:
        values = values[:-1]
    return s, values


def read_minisat(result):
    s = None
    first = True
    values = []
    with open(result, "rt") as output:
        for line in output:
            if first:
                if line.startswith("S"):
                    s = True
                else:
                    s = False
                first = False
            else:
                values += map(int, line.split())
    while len(values) > 0 and values[-1] == 0:
        values = values[:-1]
    return s, values
