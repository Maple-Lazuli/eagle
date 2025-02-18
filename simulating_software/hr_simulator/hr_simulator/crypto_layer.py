import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key, load_der_public_key
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import requests as r
import json
import base64


class CryptoLayer:
    private_key = None
    public_key = None
    ca_address = None
    key_id = None

    def __init__(self, ca_address="127.0.0.1"):
        os.system("openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048")
        os.system("openssl rsa -in private_key.pem -pubout -out public_key.pem")
        with open("private_key.pem", "rb") as private_key_file:
            self.private_key = load_pem_private_key(private_key_file.read(), password=None)
        with open("public_key.pem", "rb") as public_key_file:
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
            plain_text = self.private_key.decrypt(payload, padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None))
            return json.loads(plain_text.decode())
        else:
            return message_json

    def encrypt_message(self, message_json, key_id):
        res = r.get(f"http://{self.ca_address}:4580/key?key_id={key_id}")
        returned_key = res.json()['public_key']
        new_der_public_key = base64.b64decode(returned_key.encode())
        public_key = load_der_public_key(new_der_public_key)

        payload = json.dumps(message_json).encode()
        return public_key.encrypt(payload,
                                  padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(),
                                               label=None))

    def create_payload(self, message_json, key_id):
        payload = self.encrypt_message(message_json, key_id)
        payload = base64.b64encode(payload).decode()
        return json.dumps({"payload": payload})

    def get(self, destination):
        if destination.find("?") != -1:
            res = r.get(destination + f'&sender_key={self.key_id}')
        else:
            res = r.get(destination + f'?sender_key={self.key_id}')
        return self.decrypt_message(res.json())

    def post(self, destination, post_body, key_id):
        payload = self.encrypt_message(post_body, key_id)
        payload = base64.b64encode(payload).decode()
        res = r.post(destination, json=json.dumps({"payload": payload, "sender_key": self.key_id}))
        return self.decrypt_message(res.json())
