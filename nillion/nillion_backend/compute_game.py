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

def create_client(userkey_path, nodekey_path):
    userkey = getUserKeyFromFile(userkey_path)
    nodekey = getNodeKeyFromFile(nodekey_path)
    return create_nillion_client(userkey, nodekey)

async def main():

    parser = argparse.ArgumentParser(description="Compute game parameters.")
    # Define the required arguments using the '--' prefix
    parser.add_argument("--game_master_store_id", type=str, required=True)
    parser.add_argument("--word_provider_party_id", type=str, required=True)
    parser.add_argument("--word_provider_store_id", type=str, required=True)
    parser.add_argument("--word_guesser_party_id", type=str, required=True)
    parser.add_argument("--word_guesser_store_id", type=str, required=True)
    parser.add_argument("--program_id", type=str, required=True)

    # Parse the arguments
    args = parser.parse_args()

    # print("getting started")
    cluster_id = os.getenv("NILLION_CLUSTER_ID")

    game_master_client = create_client(chinedu["userkey_file"], chinedu["nodekey_file"])
    game_master = {"user_id":game_master_client.user_id(), "party_id":game_master_client.party_id(),
                   "party_name":"game_master"}

    # print(game_master)
    compute_bindings = nillion.ProgramBindings(args.program_id)
    compute_bindings.add_input_party(game_master["party_name"], game_master["party_id"])
    compute_bindings.add_input_party("word_provider", args.word_provider_party_id)
    compute_bindings.add_input_party("word_guesser", args.word_guesser_party_id)
    compute_bindings.add_output_party(game_master["party_name"], game_master["party_id"])

    # print(f"Computing using program {args.program_id}")
    # print(f"Use secret store_ids")

    computation_time_secrets = nillion.Secrets({})
    # nillion.Secrets({"my_int1": nillion.SecretInteger(5)})
    
    # Compute on the secret
    compute_id = await game_master_client.compute(
        cluster_id,
        compute_bindings,
        [args.game_master_store_id, args.word_provider_store_id, args.word_guesser_store_id],
        computation_time_secrets,
        nillion.PublicVariables({}),
    )

    # Print compute result
    # print(f"The computation was sent to the network. compute_id: {compute_id}")
    while True:
        compute_event = await game_master_client.next_compute_event()
        if isinstance(compute_event, nillion.ComputeFinishedEvent):
            # print(f"✅  Compute complete for compute_id {compute_event.uuid}")
            # print(f"🖥️  The result is {compute_event.result.value}")
            result = compute_event.result.value
            print("attempts_left:", result["attempts_left"])
            print("slots_guessed:", result["slots_guessed_in_attempt"])
            return compute_event.result.value

        


if __name__ == "__main__":
    asyncio.run(main())

    # python compute_game.py    --word_provider_party_id 12D3KooWQQ7v5ZYdQRAVkt2NbeEaPJX4FS2TM5jjVZkSxJqmGqt8 --word_provider_story_id af3b146d-f0c9-477f-9fdb-856f6bcbb607 --word_guesser_party_id 12D3KooWSkr3ZhqigrDTzc6MbEUcozxrvVvC4usDXbwFdozW7Qwj --word_guesser_store_id 2695e02e-aa26-400b-8069-387b94a2d3fa --program_id 5LMk2a895E9aySteoxUECxVqRBtZgh9VCjrbtXHAowqUfUWVcd5mVVZt481DLFH41VXCpz7RSzhMBEpYFSYDezEE/hangman --game_master_store_id c8cb67ce-8cf8-49ee-af20-47ef4052611a

    