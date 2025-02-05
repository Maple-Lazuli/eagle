from flask import Flask, request, Response
import json
import utilities as u

import os

app = Flask(__name__)

u.init_db()


@app.route('/get_section_ssps', methods=['GET'])
def section_ssp_assignment():
    sect_id = request.args.get('section_id')

    assigned_ssps = u.get_section_ssps(sect_id)

    return Response(json.dumps(assigned_ssps), status=200, mimetype='application/json')


@app.route('/get_division_ssps', methods=['GET'])
def division_ssp_assignment():
    division_id = request.args.get('division_id')

    assigned_ssps = u.get_division_ssps(division_id)

    return Response(json.dumps(assigned_ssps), status=200, mimetype='application/json')


@app.route('/get_ssps', methods=['GET'])
def get_ssps():
    ssps = u.get_ssp_list()
    return Response(json.dumps(ssps), status=200, mimetype='application/json')


@app.route('/get_ssp_mapping', methods=['GET'])
def get_ssps_mapping():
    ssps_mapping = u.get_ssp_list()
    return Response(json.dumps(ssps_mapping), status=200, mimetype='application/json')


@app.route('/register', methods=['POST'])
def register_ssp_use():
    if not request.is_json:
        return Response("Invalid Request", status=400, mimetype='application/json')

    data = json.loads(request.json)
    sect_id = data['section_id']

    u.assign_ssps(sect_id)
    assigned_ssps = u.get_section_ssps(sect_id)

    return Response(json.dumps(assigned_ssps), status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4520)
