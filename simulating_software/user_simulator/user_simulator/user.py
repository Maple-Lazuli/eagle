import json
import threading
import utilities as u
import random
import time
import datetime
import requests as r
import crypto_layer as cl


def set_up():
    crypto = cl.CryptoLayer()
    first_name = u.get_random_first_name()
    last_name = u.get_random_last_name()

    # res = r.post("http://127.0.0.1:4510/register", json=json.dumps({"first_name": first_name, "last_name": last_name}))
    # employee_record = res.json()

    hr_key = r.get("http://127.0.0.1:4510/key_id").json()['key_id']
    employee_record = crypto.post("http://127.0.0.1:4510/register", {"first_name": first_name, "last_name": last_name},
                                  hr_key)

    employee_num = employee_record['Employee_id']
    department_id = employee_record['Department_id']
    division_id = employee_record['Division_id']
    section_id = employee_record['Section_id']

    position_lead = employee_record['Lead_id'] == employee_num
    start_hour = employee_record['Start_Time']
    work_days = employee_record['Days']

    # res = r.post("http://127.0.0.1:4530/register",
    #              json=json.dumps({"first_name": first_name, "last_name": last_name, 'employee_num': employee_num}))
    # account_name = res.json()['account']

    it_key = r.get("http://127.0.0.1:4530/key_id").json()['key_id']
    account_name = crypto.post("http://127.0.0.1:4530/register",
                               {"first_name": first_name, "last_name": last_name, 'employee_num': employee_num,
                                "key_id": crypto.key_id}, it_key)

    ssp_key = r.get("http://127.0.0.1:4520/key_id").json()['key_id']
    if position_lead:
        # res = r.post("http://127.0.0.1:4520/register", json=json.dumps({"section_id": section_id}))
        res = crypto.post("http://127.0.0.1:4520/register", {"section_id": section_id}, ssp_key)
    else:
        # res = r.get(f"http://127.0.0.1:4520/get_section_ssps?section_id={section_id}")
        res = crypto.get(destination=f"http://127.0.0.1:4520/get_section_ssps?section_id={section_id}")

    work_ssps = [result[1] for result in res]

    insider_status = random.randint(0, 1000) == 500

    if insider_status:
        u.register_insider(account_name, crypto)

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
            "insider": insider_status,
            "crypto": crypto
            }


def main():
    user_dict = set_up()
    crypto = user_dict['crypto']
    while not u.kill_switch_active(crypto):
        time.sleep(random.randint(1, 30))
        current_time = u.get_current_sim_time(crypto)
        normal_hours = u.within_operating_hours(current_time, user_dict['start_hour'], user_dict['work_days'])
        if not normal_hours:
            time.sleep(random.randint(60*2, 60*5))
        if user_dict['insider']:

            # decide whether to go in after hours
            if not normal_hours:
                if not random.randint(0, 20) == 3:
                    continue
            # decide whether random ssp or typical ssp
            if random.randint(0, 30) == 5:
                rand_ssp = random.choice(u.get_registered_ssps(crypto))
                u.send_request(user_dict['employee_num'], rand_ssp, crypto)
            else:
                # decide dept ssp or team ssp
                if random.randint(0, 15) == 3:
                    div_ssp = random.choice(u.get_division_ssps(user_dict['division_id'], crypto))
                    u.send_request(user_dict['employee_num'], div_ssp, crypto)

                else:
                    sect_ssp = random.choice(user_dict['work_ssps'])
                    u.send_request(user_dict['employee_num'], sect_ssp, crypto)
        else:
            # decide whether to go in after hours
            if not normal_hours:
                if not random.randint(0, 30) == 3:
                    continue

            # decide dept ssp or team ssp
            if random.randint(0, 30) == 3:
                dept_ssp = random.choice(u.get_division_ssps(user_dict['division_id'], crypto))
                u.send_request(user_dict['employee_num'], dept_ssp, crypto)

            else:
                sect_ssp = random.choice(user_dict['work_ssps'])
                u.send_request(user_dict['employee_num'], sect_ssp, crypto)


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
