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


def log_storage(log: dict) -> bool:
    """
    This function writes the log event to the log storage directory.
    :param log:
    :return:
    """
    pass