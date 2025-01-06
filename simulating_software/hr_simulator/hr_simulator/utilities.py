import json
import random
import os


def register_employee(first_name, last_name, number, organization):
    departments = [_ for _ in organization.keys()]
    department = departments[random.randint(0, len(departments) - 1)]

    teams = [_ for _ in organization[department].keys()]
    team = teams[random.randint(0, len(teams) - 1)]

    employee = {
        "First_Name": first_name,
        "Last_Name": last_name,
        "Employee_Num": number,
        "Department": department,
        "Team": team
    }

    organization[department][team]["Members"].append(number)

    if organization[department][team]["Lead"] == -1:
        organization[department][team]["Lead"] = number
        organization[department][team]["Start_Time"] = random.randint(0, 23)
        organization[department][team]["Days"] = list(set([random.randint(0, 6) for _ in range(6)]))

    return employee, organization


def initialize_organization():
    with open("organization.json", "r") as file_in:
        return json.load(file_in)


def save_dictionary(path, d):
    with open(path, "w") as file_out:
        json.dump(file_out, d)


def load_dictionary(path):
    with open(path, "r") as file_out:
        return json.load(file_out)
