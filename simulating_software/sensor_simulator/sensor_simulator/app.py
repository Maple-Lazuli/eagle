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


@app.route('/testing', methods=['POST'])
def testing():
    """Logs an event and determines if access is authorized."""
    data = json.loads(request.json)
    sender_key = data["sender_key"]
    data = crypto.decrypt_message(data)
    too_big = """
    1. The Key:
Purpose: The key is the secret piece of data used to both encrypt and decrypt the data.
How to Share: In symmetric encryption, both the sender and the receiver must have access to the same key. This is the sensitive piece of information that must be protected. If an attacker gets access to the key, they can decrypt the data.
Sharing the Key: Typically, the key is shared out-of-band, meaning it is sent securely via some other means (e.g., using public-key cryptography, a secure key exchange protocol like Diffie-Hellman, or through secure channels like HTTPS). It's not sent alongside the encrypted message because anyone who intercepts the key can decrypt the data.
2. The IV (Initialization Vector):
Purpose: The IV is used to add randomness to the encryption process. It ensures that even if the same data is encrypted multiple times with the same key, the resulting ciphertext will be different each time.
How to Share: The IV does not need to be kept secret like the key. It can be sent along with the encrypted data (typically as a prefix or in a specific format). Since it's used to make encryption more secure, it’s often a good practice to send it alongside the ciphertext, but it should be unique for every encryption operation to avoid patterns that could be exploited.
Example: You can send the IV along with the ciphertext, such as in the form of a tuple (IV, ciphertext), or concatenate them together in the message.
Example of Sharing Key and IV
For secure communication, you could send the IV along with the encrypted data in this way:

Encryption:

Generate a random IV.
Encrypt the data using the key and IV.
Send both the IV and the encrypted data to the recipient.
Decryption:

The recipient receives the IV and the encrypted data.
They use the same key and IV to decrypt the data.

    """
    return Response(crypto.create_payload({"Response": too_big}, sender_key), status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4590)
