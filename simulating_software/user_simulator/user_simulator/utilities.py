import json
import random


def get_random_first_name():
    with open("./refs/first_names.json", "r") as file_in:
        return random.choice(json.load(file_in))


def get_random_last_name():
    with open("./refs/last_names.json", "r") as file_in:
        return random.choice(json.load(file_in))
