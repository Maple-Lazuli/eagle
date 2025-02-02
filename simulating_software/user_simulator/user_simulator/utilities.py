import json
import random
import datetime
import requests as r


def get_random_first_name():
    with open("./user_simulator/refs/first_names.json", "r") as file_in:
        return random.choice(json.load(file_in))


def get_random_last_name():
    with open("./user_simulator/refs/last_names.json", "r") as file_in:
        return random.choice(json.load(file_in))


def within_operating_hours(current_time, start_hour, work_days):
    current_day = current_time.weekday()

    if not ((current_day in work_days) or ((current_day - 1) % 7 in work_days)):
        return False

    start_time = datetime.datetime.strptime(f'{current_time.day}-{current_time.month}-{current_time.year}',
                                            "%d-%m-%Y") + datetime.timedelta(hours=start_hour)

    return 0 <= (current_time - start_time).seconds <= 60 * 60 * 8


def kill_switch_active():
    res = r.get(f"http://127.0.0.1:4590/kill_switch")
    return res.json()['kill_active']


def get_current_sim_time():
    res = r.get(f"http://127.0.0.1:4590/time")
    return datetime.datetime.fromtimestamp(float(res.json()['timestamp']))


def send_request(account, target, department):
    """
    Send a request to access organizational resources
    :param account:
    :param target:
    :param department:
    :return:
    """
    r.post("http://127.0.0.1:4590/event",
           json=json.dumps({'account': account, 'target': target, "department": department}))


def get_department_ssps(department):
    """
    Send a request discover ssps utilized by the department
    :param department:
    :return:
    """
    res = r.get(f"http://127.0.0.1:4520/department_ssps?department={department}")
    return res.json()


def register_insider(account_name):
    r.post("http://127.0.0.1:4590/insider",
           json=json.dumps({'account': account_name}))


def get_registered_ssps():
    res = r.get(f"http://127.0.0.1:4520/get_ssps")
    return res.json()
