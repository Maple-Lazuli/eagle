from flask import Flask, request, Response
import json
import utilities as u

import os

app = Flask(__name__)

if os.path.exists(".data"):
    ssp_mapping = u.load_dictionary(".data", "ssp_use.json")
else:
    os.mkdir(".data")
    ssp_mapping = dict()


@app.route('/ssps', methods=['GET'])
def get_ssps_mapping():
    return Response(json.dumps(ssp_mapping), status=200, mimetype='application/json')


@app.route('/department_ssps', methods=['GET'])
def get_department_ssps():
    department = request.args.get('department')
    ssps = []

    for key in ssp_mapping.keys():
        if key.find(department) != -1:
            ssps.extend(ssp_mapping[key])

    return Response(json.dumps(ssps), status=200, mimetype='application/json')


@app.route('/dept_team_ssps', methods=['GET'])
def get_ssp_mapping():
    team = request.args.get('team')
    department = request.args.get('department')
    pairing = f'{department}-{team}'
    if pairing in [_ for _ in ssp_mapping.keys()]:
        return Response(json.dumps(ssp_mapping[f'{department}-{team}']), status=200, mimetype='application/json')
    else:
        return Response(json.dumps([]), status=400, mimetype='application/json')


@app.route('/get_ssps', methods=['GET'])
def get_ssps():
    registered_ssps = []
    for key in ssp_mapping.keys():
        registered_ssps.extend(ssp_mapping[key])
    return Response(json.dumps(registered_ssps), status=200, mimetype='application/json')


@app.route('/register', methods=['POST'])
def register_ssp_use():
    global ssp_mapping
    if not request.is_json:
        return Response("Invalid Request", status=400, mimetype='application/json')

    data = json.loads(request.json)
    department = data['department']
    team = data['team']
    pairing = f'{department}-{team}'
    random_ssps = u.get_ssps()

    ssp_mapping[pairing] = random_ssps

    u.save_dictionary(".data", "ssp_use.json", ssp_mapping)

    return Response(json.dumps(random_ssps), status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4520)
