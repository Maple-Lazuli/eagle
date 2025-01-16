import json
import random
import os


def create_user_account(first_name, last_name, accounts_names):
    base_account_name = f'{first_name[0]}{last_name}'

    if base_account_name not in accounts_names:
        return base_account_name
    else:
        index = 1
        base_account_name_numeric = base_account_name + str(index)
        while base_account_name_numeric in accounts_names:
            index += 1
            base_account_name_numeric = base_account_name + str(index)
        return base_account_name_numeric


def save_dictionary(directory, file_name, d):
    path = os.path.join(directory, file_name)
    with open(path, "w") as file_out:
        json.dump(d, file_out)


def load_dictionary(directory, file_name):
    path = os.path.join(directory, file_name)
    with open(path, "r") as file_out:
        return json.load(file_out)

