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


def kill_switch_active(crypto):
    res = crypto.get(f"http://127.0.0.1:4590/kill_switch")
    return res['kill_active']


def get_current_sim_time(crypto):
    res = crypto.get(f"http://127.0.0.1:4590/time")
    return datetime.datetime.fromtimestamp(float(res['timestamp']))


def send_request(employee_num, target, crypto):
    """
    Send a request to access organizational resources
    :param employee_num:
    :param target:
    :return:
    """

    sensor_key = r.get("http://127.0.0.1:4590/key_id").json()['key_id']
    crypto.post("http://127.0.0.1:4590/event", {'emp_id': employee_num, 'ssp_id': target}, sensor_key)


def get_division_ssps(division_id, crypto):
    """
    Send a request discover ssps utilized by the department
    :param division_id:
    :return:
    """
    res = crypto.get(f"http://127.0.0.1:4520/get_division_ssps?division_id={division_id}")
    return [result[1] for result in res]  # filter for ssp_ids only


def register_insider(account_name, crypto):
    sensor_key = r.get("http://127.0.0.1:4590/key_id").json()['key_id']
    crypto.post("http://127.0.0.1:4590/insider", {'account': account_name}, sensor_key)


def get_registered_ssps(crypto):
    res = crypto.get(f"http://127.0.0.1:4520/get_ssps")
    return [result[0] for result in res]  # filter for ssp_ids only
