import asyncio
import argparse
import py_nillion_client as nillion
import os
import sys
import pytest
from config import adaobi, bisi, chinedu
from collections import namedtuple



from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helpers.nillion_client_helper import create_nillion_client
from helpers.nillion_keypath_helper import getUserKeyFromFile, getNodeKeyFromFile

load_dotenv()
Program = namedtuple("Program", ["action_id", "program_id", "program_name"])

def create_client(userkey_path, nodekey_path):
    userkey = getUserKeyFromFile(userkey_path)
    nodekey = getNodeKeyFromFile(nodekey_path)
    return create_nillion_client(userkey, nodekey)

async def store_program(cluster_id, client, user_id, program_name, base_dir):
    
    program_mir_path=f"{base_dir}/nillion/programs-compiled/{program_name}.nada.bin"

    # store program
    action_id = await client.store_program(
        cluster_id, program_name, program_mir_path
    )

    program_id=f"{user_id}/{program_name}"
    return Program(action_id, program_id, program_name)


async def main():
    parser = argparse.ArgumentParser(description="Collect and process game parameters.")

    # Define the required arguments using the '--' prefix
    parser.add_argument("--operation", type=str, required=True)
    parser.add_argument("--program_id", type=str, required=True)
    parser.add_argument("--attempts", type=str, required=True)

    # Parse the arguments
    args = parser.parse_args()

    cluster_id = os.getenv("NILLION_CLUSTER_ID")

    game_master_client = create_client(chinedu["userkey_file"], chinedu["nodekey_file"])
    game_master = {"user_id":game_master_client.user_id(), "party_id":game_master_client.party_id(),
                   "party_name":"game_master"}
    
    if args.operation == "store":

        stored_secret_array = nillion.Secrets(
            {  
                "attempts_left": nillion.SecretInteger(int(args.attempts))
                }
            )
        
        secret_bindings = nillion.ProgramBindings(args.program_id)
        secret_bindings.add_input_party(game_master["party_name"], game_master["party_id"])

        # Store a secret array
        game_master_store_id = await game_master_client.store_secrets(
            cluster_id, secret_bindings, stored_secret_array, None
        )

        print("game_master_storeid:", game_master_store_id)



if __name__ == "__main__":
    asyncio.run(main())