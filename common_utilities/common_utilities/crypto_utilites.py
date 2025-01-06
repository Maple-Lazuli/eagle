import binascii
import struct

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import pickle


def encrypt(key, data, iv):
    cfb = AES.new(key, AES.MODE_CFB, iv)
    return cfb.encrypt(data)


def decrypt(key, data, iv):
    cfb = AES.new(key, AES.MODE_CFB, iv)
    return cfb.decrypt(data)


def get_pem_parameters(file_path):
    with open(file_path, "rb") as key_file:
        private_key = load_pem_private_key(
            key_file.read(), password=None, backend=default_backend()
        )
    modulus = private_key.public_key().public_numbers().n
    public_exponent = private_key.public_key().public_numbers().e
    private_exponent = private_key.private_numbers().d
    prime1 = private_key.private_numbers().p
    prime2 = private_key.private_numbers().q

    return {
        'n': modulus,
        'e': public_exponent,
        'd': private_exponent
    }


def rsa_encrypt(message, public_key):
    ciphertext = pow_mod(message, public_key['e'], public_key['n'])
    return ciphertext.to_bytes((public_key['n'].bit_length() + 7) // 8, "big")


def rsa_decrypt(message, public_key):
    ciphertext = pow_mod(message, public_key['d'], public_key['n'])
    return ciphertext.to_bytes((public_key['n'].bit_length() + 7) // 8, "big")


def pow_mod(base, exp, mod):
    if mod == 1:
        return 0
    else:
        result = 1
        while exp > 0:
            if exp & 1:
                result = (result * base) % mod
            exp = exp >> 1
            base = (base * base) % mod
        return result
