import json
import threading
import utilities as u
import random
import time
import datetime
import requests as r


def set_up():
    first_name = u.get_random_first_name()
    last_name = u.get_random_last_name()

    res = r.post("http://127.0.0.1:4510/register", json=json.dumps({"first_name": first_name, "last_name": last_name}))

    employee_record = res.json()

    employee_num = employee_record['Employee_id']
    department_id = employee_record['Department_id']
    division_id = employee_record['Division_id']
    section_id = employee_record['Section_id']

    position_lead = employee_record['Lead_id'] == employee_num
    start_hour = employee_record['Start_Time']
    work_days = employee_record['Days']

    res = r.post("http://127.0.0.1:4530/register",
                 json=json.dumps({"first_name": first_name, "last_name": last_name, 'employee_num': employee_num}))

    account_name = res.json()['account']

    if position_lead:
        res = r.post("http://127.0.0.1:4520/register", json=json.dumps({"section_id": section_id}))
    else:
        res = r.get(f"http://127.0.0.1:4520/get_section_ssps?section_id={section_id}")

    work_ssps = [result[1] for result in res.json()]

    insider_status = random.randint(0, 1000) == 500

    if insider_status:
        u.register_insider(account_name)

    return {"first_name": first_name,
            "last_name": last_name,
            "employee_num": employee_num,
            "department_id": department_id,
            "section_id": section_id,
            "division_id": division_id,
            "position_lead": position_lead,
            "start_hour": start_hour,
            "work_days": work_days,
            "account_name": account_name,
            "work_ssps": work_ssps,
            "insider": insider_status
            }


def main():
    user_dict = set_up()
    while not u.kill_switch_active():
        time.sleep(random.randint(3, 10))
        current_time = u.get_current_sim_time()
        normal_hours = u.within_operating_hours(current_time, user_dict['start_hour'], user_dict['work_days'])
        if not normal_hours:
            time.sleep(random.randint(20, 60))

        if user_dict['insider']:

            # decide whether to go in after hours
            if not normal_hours:
                if not random.randint(0, 20) == 3:
                    continue
            # decide whether random ssp or typical ssp
            if random.randint(0, 30) == 5:
                rand_ssp = random.choice(u.get_registered_ssps())
                u.send_request(user_dict['employee_num'], rand_ssp)
            else:
                # decide dept ssp or team ssp
                if random.randint(0, 15) == 3:
                    div_ssp = random.choice(u.get_division_ssps(user_dict['division_id']))
                    u.send_request(user_dict['employee_num'], div_ssp)

                else:
                    sect_ssp = random.choice(user_dict['work_ssps'])
                    u.send_request(user_dict['employee_num'], sect_ssp)
        else:
            # decide whether to go in after hours
            if not normal_hours:
                if not random.randint(0, 30) == 3:
                    continue

            # decide dept ssp or team ssp
            if random.randint(0, 30) == 3:
                dept_ssp = random.choice(u.get_division_ssps(user_dict['division_id']))
                u.send_request(user_dict['employee_num'], dept_ssp)

            else:
                sect_ssp = random.choice(user_dict['work_ssps'])
                u.send_request(user_dict['employee_num'], sect_ssp)


def multi_thread_users(num_users):
    threads = []

    for _ in range(num_users):
        time.sleep(random.randint(1, 5))
        thread = threading.Thread(target=main)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    #main()
    multi_thread_users(5)
