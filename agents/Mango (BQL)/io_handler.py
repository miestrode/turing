# Name: Yehonatan Sofri
# ID:   205433329


import cPickle as pickle
import os.path
import os


prefix = "./data/"


class IOHandler:
    def __init__(self):
        os.mkdir(prefix)

    @staticmethod
    def read(file_name):
        file_name = prefix + file_name
        data = None
        try:
            output = open(file_name, "rb")
            data = pickle.load(output)
            output.close()
        except IOError:
            data = None
        return data

    @staticmethod
    def write(file_name, obj):
        file_name = prefix + file_name
        output = open(file_name, "wb")
        pickle.dump(obj, output)
        output.close()

    @staticmethod
    def append_to_file(file_name, data_string):
        file_name = prefix + file_name
        if os.path.exists(file_name):
            append_write = "a"  # append if already exists
        else:
            append_write = "w"  # make a new file if not

        my_file = open(file_name, append_write)
        my_file.write(data_string + "\n")
        my_file.close()
