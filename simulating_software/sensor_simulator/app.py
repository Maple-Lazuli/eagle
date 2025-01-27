from flask import Flask, request, Response
import json

import os

app = Flask(__name__)

if not os.path.exists(".data"):
    os.mkdir(".data")


@app.route('/logs', methods=['GET'])
def get_logs():


    if pairing in [_ for _ in ssp_mapping.keys()]:
        return Response(json.dumps(ssp_mapping[f'{department}-{team}']), status=200, mimetype='application/json')
    else:
        return Response(json.dumps([]), status=400, mimetype='application/json')


@app.route('/event', methods=['POST'])
def register_ssp_use():
    if not request.is_json:
        return Response("Invalid Request", status=400, mimetype='application/json')

    data = json.loads(request.json)

    u.save_log(".data")

    return Response("Received", status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(port=4520)
