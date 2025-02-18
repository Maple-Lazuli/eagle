from flask import Flask, request, Response
import json
import datetime
import crypto_layer as cl
import utilities as u

app = Flask(__name__)

u.init_db()

# time_scale = 1.00000001
# time_scale = 1.0000001
time_scale = 1.0000001
current = datetime.datetime.now()
scaled_base = current.timestamp() * time_scale
kill_switch_active = False

crypto = cl.CryptoLayer()


def get_scaled_timestamp():
    global current
    global scaled_base
    seconds = (datetime.datetime.now() - current).seconds
    scaled = scaled_base
    for i in range(seconds):
        scaled *= time_scale
    return scaled


@app.route('/key_id', methods=['GET'])
def get_key_id():
    return Response(json.dumps({'key_id': crypto.key_id}), status=200, mimetype='application/json')


@app.route('/insider', methods=['POST'])
def register_insider():
    """Registers an insider threat."""
    data = json.loads(request.json)
    sender_key = data["sender_key"]
    data = crypto.decrypt_message(data)
    account = data['account']
    u.register_insider(account)

    return Response(crypto.create_payload({"Response": "Okay"}, sender_key), status=200, mimetype='application/json')


@app.route('/insider', methods=['GET'])
def get_insiders():
    """Retrieves a list of registered insider threats."""
    sender_key = request.args.get('sender_key')

    insiders = u.get_insiders()

    return Response(crypto.create_payload(insiders, sender_key), status=200, mimetype='application/json')


@app.route('/kill_switch', methods=['GET'])
def get_kill_status():
    sender_key = request.args.get('sender_key')

    response = {'kill_active': kill_switch_active}

    return Response(crypto.create_payload(response, sender_key), status=200, mimetype='application/json')


@app.route('/kill_switch_toggle', methods=['GET'])
def set_kill_switch():
    global kill_switch_active
    kill_switch_active = not kill_switch_active
    return Response(json.dumps({'kill_active': kill_switch_active}), status=200, mimetype='application/json')


@app.route('/time', methods=['GET'])
def get_time():
    scaled = get_scaled_timestamp()

    sender_key = request.args.get('sender_key')

    response = {'timestamp': scaled}

    return Response(crypto.create_payload(response, sender_key), status=200, mimetype='application/json')


@app.route('/logs', methods=['GET'])
def get_logs():
    """Retrieves logged events."""
    logs = u.get_logs()

    sender_key = request.args.get('sender_key')

    return Response(crypto.create_payload(logs, sender_key), status=200, mimetype='application/json')


@app.route('/event', methods=['POST'])
def archive_event():
    """Logs an event and determines if access is authorized."""
    data = json.loads(request.json)
    sender_key = data["sender_key"]
    data = crypto.decrypt_message(data)
    timestamp = get_scaled_timestamp()
    emp_id = data['emp_id']
    ssp_id = data['ssp_id']

    u.insert_log(timestamp, emp_id, ssp_id)

    return Response(crypto.create_payload({"Response": "Okay"}, sender_key), status=200, mimetype='application/json')



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4590)
