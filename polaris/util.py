
import os
import imp


def fill_ro(string):
    return string.replace("^ro", "^r")


def import_file(filename):
    (path, name) = os.path.split(filename)
    (name, ext) = os.path.splitext(name)

    (file, filename, data) = imp.find_module(name, [path])
    return imp.load_module(name, file, filename, data)


def dict_sum_latter_wins(d1, d2):
    if d1 is None:
        return d2
    if d2 is None:
        return d1
    try:
        d1 + d2
        return d2
    except TypeError:
        # assume d1 and d2 are dictionaries
        keys = set(d1.iterkeys()) | set(d2.iterkeys())
        return dict((key, dict_sum_latter_wins(d1.get(key), d2.get(key))) for key in keys)

