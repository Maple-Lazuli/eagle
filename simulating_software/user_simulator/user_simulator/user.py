import json

import utilities as u
import random
import time
import datetime
import requests as r


def set_up():
    first_name = u.get_random_first_name()
    last_name = u.get_random_last_name()

    res = r.post("http://127.0.0.1:4510/register", json=json.dumps({"first_name": first_name, "last_name": last_name}))

    employee_record = res.json()[0]
    team_record = res.json()[1]

    employee_num = employee_record['Employee_Num']
    department = employee_record['Department']
    team = employee_record['Team']

    position_lead = team_record['Lead'] == employee_num
    start_hour = team_record['Start_Time']
    work_days = team_record['Days']

    res = r.post("http://127.0.0.1:4530/register",
                 json=json.dumps({"first_name": first_name, "last_name": last_name, 'employee_num': employee_num}))

    account_name = res.json()['account']

    if position_lead:
        res = r.post("http://127.0.0.1:4520/register", json=json.dumps({"department": department, "team": team}))
    else:
        res = r.get(f"http://127.0.0.1:4520/dept_team_ssps?team={team}&department={department}")

    work_ssps = res.json()

    insider_status = random.randint(0, 1000) == 500

    if insider_status:
        u.register_insider(account_name)

    return {"first_name": first_name,
            "last_name": last_name,
            "employee_num": employee_num,
            "department": department,
            "team": team,
            "position_lead": position_lead,
            "start_hour": start_hour,
            "work_days": work_days,
            "account_name": account_name,
            "work_ssps": work_ssps
            }


def main():
    user_dict = set_up()

    while not u.kill_switch_active():
        time.sleep(random.randint(3, 10))
        current_time = u.get_current_sim_time()
        normal_hours = u.within_operating_hours(current_time, user_dict['start_hour'], user_dict['work_days'])

        if user_dict['insider']:

            # decide whether to go in after hours
            if not normal_hours:
                if not random.randint(0, 20) == 3:
                    continue
            # decide whether random ssp or typical ssp
            if random.randint(0, 30) == 5:
                rand_ssp = random.choice(u.get_registered_ssps())
                u.send_request(user_dict['account_name'], rand_ssp, user_dict['department'])
            else:
                # decide dept ssp or team ssp
                if random.randint(0, 15) == 3:
                    dept_ssp = random.choice(u.get_department_ssps(user_dict['department']))
                    u.send_request(user_dict['account_name'], dept_ssp, user_dict['department'])

                else:
                    team_ssp = random.choice(user_dict['work_ssps'])
                    u.send_request(user_dict['account_name'], team_ssp, user_dict['department'])
        else:
            # decide whether to go in after hours
            if not normal_hours:
                if not random.randint(0, 30) == 3:
                    continue

            # decide dept ssp or team ssp
            if random.randint(0, 30) == 3:
                dept_ssp = random.choice(u.get_department_ssps(user_dict['department']))
                u.send_request(user_dict['account_name'], dept_ssp, user_dict['department'])

            else:
                team_ssp = random.choice(user_dict['work_ssps'])
                u.send_request(user_dict['account_name'], team_ssp, user_dict['department'])


if __name__ == "__main__":
    main()
