import os
import py_nillion_client as nillion
from dotenv import load_dotenv
load_dotenv()


chinedu = {
    "userkey_file": os.getenv("NILLION_USERKEY_PATH_PARTY_1"),
    "nodekey_file": os.getenv("NILLION_NODEKEY_PATH_PARTY_1"),
    "nodekey_alternate_file": os.getenv("NILLION_NODEKEY_PATH_PARTY_4"),
}

# Bob and Charlie

adaobi = {
        "userkey_file": os.getenv("NILLION_USERKEY_PATH_PARTY_2"),
        "nodekey_file": os.getenv("NILLION_NODEKEY_PATH_PARTY_2"),
    }

bisi =    {
        "userkey_file": os.getenv("NILLION_USERKEY_PATH_PARTY_3"),
        "nodekey_file": os.getenv("NILLION_NODEKEY_PATH_PARTY_3"),
    }