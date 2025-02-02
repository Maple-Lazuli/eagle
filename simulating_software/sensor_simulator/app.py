from flask import Flask, request, Response
import requests as r
import json
import utilities as u
import datetime
import os

app = Flask(__name__)

if not os.path.exists(".data"):
    os.mkdir(".data")

# time_scale = 1.00000001
# time_scale = 1.0000001
time_scale = 1.0000001
current = datetime.datetime.now()
scaled_base = current.timestamp() * time_scale

ssps_by_department = dict()
kill_switch_active = False
insiders = []


@app.route('/insider', methods=['POST'])
def register_insider():
    global insiders
    data = json.loads(request.json)
    insiders.append(data['account'])
    return Response("Okay", status=200, mimetype='application/json')


@app.route('/insider', methods=['GET'])
def get_insiders():
    global insiders
    return Response(json.dumps(insiders), status=200, mimetype='application/json')


@app.route('/kill_switch', methods=['GET'])
def get_kill_status():
    return Response(json.dumps({'kill_active': kill_switch_active}), status=200, mimetype='application/json')


@app.route('/kill_switch_toggle', methods=['GET'])
def set_kill_switch():
    global kill_switch_active

    kill_switch_active = not kill_switch_active

    return Response(json.dumps({'kill_active': kill_switch_active}), status=200, mimetype='application/json')


@app.route('/time', methods=['GET'])
def get_time():
    global current
    global scaled_base
    seconds = (datetime.datetime.now() - current).seconds
    scaled = scaled_base
    for i in range(seconds):
        scaled *= time_scale

    return Response(json.dumps({'timestamp': scaled}), status=200, mimetype='application/json')


@app.route('/logs', methods=['GET'])
def get_logs():
    logs = u.aggregate_logs(".data")

    return Response(json.dumps(logs), status=200, mimetype='application/json')


@app.route('/event', methods=['POST'])
def archive_event():
    global ssps_by_department
    if not request.is_json:
        return Response("Invalid Request", status=400, mimetype='application/json')

    data = json.loads(request.json)

    # light authentication mechanism
    authorized = u.lookup_ssp_by_department(ssps_by_department, data['target'], data['department'])

    if not authorized:
        ssp_maintainer_res = r.get(f"http://127.0.0.1:4520/department_ssps?department={data['department']}")
        dept_ssps = ssp_maintainer_res.json()
        ssps_by_department[data['department']] = dept_ssps

        authorized = u.lookup_ssp_by_department(ssps_by_department, data['target'], data['department'])

    data['authorized'] = authorized

    u.save_dictionary(".data", data)

    return Response("Received", status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(port=4590)
