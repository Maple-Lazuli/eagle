from flask import Flask, request, Response
import json
import utilities as u
import datetime
import os

app = Flask(__name__)

if not os.path.exists(".data"):
    os.mkdir(".data")

time_scale = 1.00000001
time_scale = 1.0000001
time_scale = 1.000001
current = datetime.datetime.now()
scaled = current.timestamp() * time_scale


@app.route('/time', methds=['GET'])
def get_time():
    global current
    global scaled
    current = datetime.datetime.now() - current
    scaled = current.timestamp() * time_scale
    return Response(json.dumps({'timestamp': scaled}), status=200, mimetype='application/json')


@app.route('/logs', methods=['GET'])
def get_logs():
    logs = u.aggregate_logs(".data")

    return Response(json.dumps(logs), status=200, mimetype='application/json')


@app.route('/event', methods=['POST'])
def archive_event():
    if not request.is_json:
        return Response("Invalid Request", status=400, mimetype='application/json')

    data = json.loads(request.json)

    u.save_dictionary(".data", data)

    return Response("Received", status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(port=4590)
