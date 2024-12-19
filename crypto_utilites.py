from Crypto.PublicKey import RSA

with open("public_key.pem", "r") as key_file:
    public_key = RSA.import_key(key_file.read())

print("Public Key Loaded Successfully")
