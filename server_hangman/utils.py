import json
import threading

lock = threading.Lock()

def dump_json_safe(data, file_path):
    with lock:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)


def load_json_safe(file_path):
    with lock:
        with open(file_path, 'r') as f:
            return json.load(f)
