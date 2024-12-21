import constants as cnst
import pickle
from datetime import datetime
from hashlib import sha256
import struct
import os

def log_decryption(encrypted_log: bytes) -> dict:
    """
    Decryps the log file and returs it as a dictonary.
    :param encrypted_log: the transmitted bytes from the client
    :return: dictonary of the encrypted log
    """
    pass


def log_verification(log: dict) -> bool:
    """
    This function validates the log structure prior to the log be written to disk
    :param log: expects a log dictionary
    :return: boolean indicating the log is correctly structured.
    """
    pass


def log_storage(log: dict):
    """
    This function writes the log event to the log storage directory.
    :param log:
    :return:
    """
    timestamp = datetime.now().timestamp()
    time_bytes = struct.pack('f',timestamp)
    digest = sha256(time_bytes).hexdigest()
    log_file_name = f'{digest}.pkl'
    file_path = os.path.join(cnst.log_storage_directory,log_file_name)
    with open(file_path, "wb") as file_out:
        pickle.dump(log, file_out)
