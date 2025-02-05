from flask import Flask, request, Response
import json
import psycopg2
import datetime
import utilities as u
import requests as r

app = Flask(__name__)

u.init_db()

# time_scale = 1.00000001
# time_scale = 1.0000001
time_scale = 1.0000001
current = datetime.datetime.now()
scaled_base = current.timestamp() * time_scale
kill_switch_active = False


def get_scaled_timestamp():
    global current
    global scaled_base
    seconds = (datetime.datetime.now() - current).seconds
    scaled = scaled_base
    for i in range(seconds):
        scaled *= time_scale
    return scaled


@app.route('/insider', methods=['POST'])
def register_insider():
    """Registers an insider threat."""
    data = json.loads(request.json)
    account = data['account']
    u.register_insider(account)
    return Response("Okay", status=200, mimetype='application/json')


@app.route('/insider', methods=['GET'])
def get_insiders():
    """Retrieves a list of registered insider threats."""
    insiders = u.get_insiders()
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
    scaled = get_scaled_timestamp()

    return Response(json.dumps({'timestamp': scaled}), status=200, mimetype='application/json')


@app.route('/logs', methods=['GET'])
def get_logs():
    """Retrieves logged events."""
    logs = u.get_logs()
    return Response(json.dumps(logs), status=200, mimetype='application/json')


@app.route('/event', methods=['POST'])
def archive_event():
    """Logs an event and determines if access is authorized."""
    data = json.loads(request.json)
    timestamp = get_scaled_timestamp()
    emp_id = data['emp_id']
    ssp_id = data['ssp_id']
    u.insert_log(timestamp, emp_id, ssp_id)

    return Response("Okay", status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4590)
