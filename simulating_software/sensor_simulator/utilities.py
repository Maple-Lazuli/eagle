import hashlib
import datetime
import random
import json
import os


def save_dictionary(directory, data):
    """
    Takes the log and writes to the directory as a json object
    :param directory:
    :param data:
    :return:
    """

    now = datetime.datetime.now()
    byte_stream = str(now.timestamp()).encode() + random.randbytes(32)
    hasher = hashlib.sha3_512()
    hasher.update(byte_stream)
    file_name = hasher.hexdigest() + ".json"

    with open(os.path.join(directory, file_name), "w") as file_out:
        json.dump(data, file_out)
