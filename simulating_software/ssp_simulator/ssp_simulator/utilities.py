import json
import random
import os


def get_ssps():
    ssps = load_dictionary("./ssp_simulator", "ssp_names.json")
    num_ssps = random.randint(3, 50)
    chosen_ssps = set()
    for _ in range(num_ssps):
        chosen_ssps.add(ssps[random.randint(0, len(ssps) - 1)])
    return list(chosen_ssps)


def save_dictionary(directory, file_name, d):
    path = os.path.join(directory, file_name)
    with open(path, "w") as file_out:
        json.dump(d, file_out)


def load_dictionary(directory, file_name):
    path = os.path.join(directory, file_name)
    with open(path, "r") as file_out:
        return json.load(file_out)
