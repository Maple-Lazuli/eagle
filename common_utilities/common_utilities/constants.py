import os

log_storage_directory = "./logs"
software_event_log_director = "./software_events"

client_log_template = {
    "host_name": None,
    "host_ip": None,
    "remote_host": None,
    "remote_ip": None,
    "time": None
}


def prepare_disk() -> bool:
    try:
        if not os.path.exists(log_storage_directory):
            os.mkdir(log_storage_directory)

        if not os.path.exists(software_event_log_director):
            os.mkdir(software_event_log_director)
        return True
    except:
        return False
