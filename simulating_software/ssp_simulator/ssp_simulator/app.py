from flask import Flask, request, Response
import json
import utilities as u
import crypto_layer as cl

import os

app = Flask(__name__)

u.init_db()
crypto = cl.CryptoLayer()


@app.route('/key_id', methods=['GET'])
def get_key_id():
    return Response(json.dumps({'key_id': crypto.key_id}), status=200, mimetype='application/json')


@app.route('/get_section_ssps', methods=['GET'])
def section_ssp_assignment():
    sender_key = request.args.get('sender_key')
    sect_id = request.args.get('section_id')

    assigned_ssps = u.get_section_ssps(sect_id)

    return Response(crypto.create_payload(assigned_ssps, sender_key), status=200, mimetype='application/json')


@app.route('/get_division_ssps', methods=['GET'])
def division_ssp_assignment():
    sender_key = request.args.get('sender_key')
    division_id = request.args.get('division_id')

    assigned_ssps = u.get_division_ssps(division_id)

    return Response(crypto.create_payload(assigned_ssps, sender_key), status=200, mimetype='application/json')


@app.route('/get_ssps', methods=['GET'])
def get_ssps():
    sender_key = request.args.get('sender_key')
    ssps = u.get_ssp_list()
    return Response(crypto.create_payload(ssps, sender_key), status=200, mimetype='application/json')


@app.route('/get_ssp_mapping', methods=['GET'])
def get_ssps_mapping():
    sender_key = request.args.get('sender_key')
    ssps_mapping = u.get_ssp_list()
    return Response(crypto.create_payload(ssps_mapping, sender_key), status=200, mimetype='application/json')


@app.route('/register', methods=['POST'])
def register_ssp_use():
    if not request.is_json:
        return Response("Invalid Request", status=400, mimetype='application/json')

    data = json.loads(request.json)
    sender_key = data["sender_key"]
    data = crypto.decrypt_message(data)
    sect_id = data['section_id']
    u.assign_ssps(sect_id)
    assigned_ssps = u.get_section_ssps(sect_id)

    return Response(crypto.create_payload(assigned_ssps, sender_key), status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4520)
