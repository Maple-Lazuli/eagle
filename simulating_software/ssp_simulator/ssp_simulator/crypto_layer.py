import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key, load_der_public_key
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.backends import default_backend
import requests as r
import secrets
import json
import base64


def symmetric_encrypt(data, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padding_length = 16 - (len(data) % 16)
    padded_data = data + bytes([padding_length]) * padding_length
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return encrypted_data


def decrypt_data(data, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_data = decryptor.update(data) + decryptor.finalize()

    # Remove padding
    padding_length = decrypted_data[-1]
    original_data = decrypted_data[:-padding_length]

    return original_data


class CryptoLayer:
    private_key = None
    public_key = None
    ca_address = None
    key_id = None

    def __init__(self, ca_address="127.0.0.1"):

        key_base_name = secrets.token_hex(32)
        private_name = f"private-{key_base_name}.pem"
        public_name = f"public-{key_base_name}.pem"

        os.system(f"openssl genpkey -algorithm RSA -out {private_name} -pkeyopt rsa_keygen_bits:2048")
        os.system(f"openssl rsa -in {private_name} -pubout -out {public_name}")

        with open(private_name, "rb") as private_key_file:
            self.private_key = load_pem_private_key(private_key_file.read(), password=None)
        with open(public_name, "rb") as public_key_file:
            self.public_key = load_pem_public_key(public_key_file.read())

        self.ca_address = ca_address

        self.register_public_key()

    def register_public_key(self):
        der_public_key = self.public_key.public_bytes(encoding=Encoding.DER, format=PublicFormat.SubjectPublicKeyInfo)

        encoded = base64.b64encode(der_public_key).decode()

        res = r.post(f"http://{self.ca_address}:4580/key", json=json.dumps({"public_key": encoded}))

        self.key_id = res.json()['key_id']

    def decrypt_message(self, message_json):
        if "payload" in message_json.keys():

            payload = base64.b64decode(message_json['payload'])
            symmetric_key = base64.b64decode(message_json['symmetric_key'])

            decrypted_symmetric_key = self.private_key.decrypt(symmetric_key, padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None))

            decrypted_symmetric_key = json.loads(decrypted_symmetric_key.decode())

            key = decrypted_symmetric_key["key"]
            key = base64.b64decode(key)
            iv = decrypted_symmetric_key['iv']
            iv = base64.b64decode(iv)
            plain_text = decrypt_data(payload, key, iv)

            return json.loads(plain_text.decode())

        else:

            return message_json

    def encrypt_message(self, message_json, key_id):
        res = r.get(f"http://{self.ca_address}:4580/key?key_id={key_id}")
        returned_key = res.json()['public_key']

        new_der_public_key = base64.b64decode(returned_key.encode())
        public_key = load_der_public_key(new_der_public_key)

        key = secrets.token_bytes(32)
        key_64 = base64.b64encode(key).decode()
        iv = secrets.token_bytes(16)
        iv_64 = base64.b64encode(iv).decode()

        symmetric_key_str = json.dumps({"key": key_64, "iv": iv_64}).encode()
        symmetric_key_crypt = public_key.encrypt(symmetric_key_str,
                                                 padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                              algorithm=hashes.SHA256(),
                                                              label=None))

        payload_crypt = symmetric_encrypt(json.dumps(message_json).encode(), key, iv)

        return symmetric_key_crypt, payload_crypt

    def create_payload(self, message_json, key_id):
        symmetric_key, payload = self.encrypt_message(message_json, key_id)
        payload = base64.b64encode(payload).decode()
        symmetric_key = base64.b64encode(symmetric_key).decode()

        return json.dumps({"symmetric_key": symmetric_key, "payload": payload})

    def get(self, destination):
        if destination.find("?") != -1:
            res = r.get(destination + f'&sender_key={self.key_id}')
        else:
            res = r.get(destination + f'?sender_key={self.key_id}')
        return self.decrypt_message(res.json())

    def post(self, destination, post_body, key_id):
        symmetric_key, payload = self.encrypt_message(post_body, key_id)
        payload = base64.b64encode(payload).decode()
        symmetric_key = base64.b64encode(symmetric_key).decode()
        res = r.post(destination,
                     json=json.dumps({"symmetric_key": symmetric_key, "payload": payload, "sender_key": self.key_id}))
        return self.decrypt_message(res.json())
