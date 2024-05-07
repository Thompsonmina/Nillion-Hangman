import argparse
import asyncio
import py_nillion_client as nillion
import os
import sys
from collections import namedtuple


from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()


# utils
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def getUserKeyFromFile(userkey_filepath):
    return nillion.UserKey.from_file(userkey_filepath)

def getNodeKeyFromFile(nodekey_filepath):
    return nillion.NodeKey.from_file(nodekey_filepath)

def create_payments_config():
    return nillion.PaymentsConfig(
        os.getenv("NILLION_BLOCKCHAIN_RPC_ENDPOINT"),
        os.getenv("NILLION_WALLET_PRIVATE_KEY"),
        int(os.getenv("NILLION_CHAIN_ID")),
        os.getenv("NILLION_PAYMENTS_SC_ADDRESS"),
        os.getenv("NILLION_BLINDING_FACTORS_MANAGER_SC_ADDRESS"),
    )

def create_nillion_client(userkey, nodekey):
    bootnodes = [os.getenv("NILLION_BOOTNODE_MULTIADDRESS")]
    payments_config = create_payments_config()

    return nillion.NillionClient(
        nodekey,
        bootnodes,
        nillion.ConnectionMode.relay(),
        userkey,
        payments_config,
    )

def create_client(userkey_path, nodekey_path):
    userkey = getUserKeyFromFile(userkey_path)
    nodekey = getNodeKeyFromFile(nodekey_path)
    return create_nillion_client(userkey, nodekey)

async def delegate_permission_and_store_secret(cluster_id, client, client_dict, secret_obj, delegate_user_id, program_id):
    # Create input bindings for the program
    secret_bindings = nillion.ProgramBindings(program_id)
    secret_bindings.add_input_party(client_dict["party_name"], client_dict["party_id"])

    # Create permissions object
    permissions = nillion.Permissions.default_for_user(client_dict["user_id"])

    # Give compute permissions to the first party
    compute_permissions = {
        delegate_user_id: {program_id},
    }
    permissions.add_compute_permissions(compute_permissions)

    # Store the permissioned secret
    store_id = await client.store_secrets(
        cluster_id, secret_bindings, secret_obj, permissions
    )

    # print(f"\n🎉Party {client_dict['party_id']} stored secret  at store id: {store_id}")
    # print(f"\n🎉Word stored and compute permission on your word granted to user_id: {delegate_user_id}")

    # print("make sure to take note of your store id and party id as you will need to submit them to the game master")

    return store_id, client_dict['party_id']

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def word_to_positions(word):
    # Convert the word to lowercase
    word = word.lower()
    # Create a list of positions based on the alphabetic order, 'a' is 1, 'b' is 2, ..., 'z' is 26
    positions = [ord(char) - ord('a') + 1 for char in word if 'a' <= char <= 'z']
    return positions


async def main():
    parser = argparse.ArgumentParser(description="Collect and process game parameters.")

    # Define the required arguments using the '--' prefix
    parser.add_argument("--userkey", type=str, required=True, help="User key for authentication")
    parser.add_argument("--nodekey", type=str, required=True, help="Node key for node identification")
    parser.add_argument("--guess", type=str, required=True, help="The secret word for the hangman game")
    parser.add_argument("--game_master_id", type=str, required=True, help="Identifier for the game master")
    parser.add_argument("--program_id", type=str, required=True, help="Program identifier")
    parser.add_argument("--cluster_id", type=str, required=True, help="Cluster identifier")

    # Parse the arguments
    args = parser.parse_args()

    # print(f"User Key: {args.userkey}")
    # print(f"Node Key: {args.nodekey}")
    # print(f"Word: {args.word}")
    # print(f"Game Master ID: {args.game_master_id}")
    # print(f"Program ID: {args.program_id}")
    # print(f"Cluster ID: {args.cluster_id}")

    word_guesser_client = create_client(args.userkey, args.nodekey)
    word_guesser = {"user_id":word_guesser_client.user_id(), "party_id":word_guesser_client.party_id(),
                   "party_name":"word_guesser"}

    
    guess_as_int = word_to_positions(args.guess)[0]
    # print(guess_as_int)

    
    secret_guess = nillion.Secrets(
        {
            "guessed_letter": nillion.SecretInteger(guess_as_int),
        }
    )

    store_id, client_id = await delegate_permission_and_store_secret(args.cluster_id, word_guesser_client,
                        word_guesser, secret_guess, args.game_master_id, args.program_id)
    

    print("store_id:", store_id)
    print("party_id:", client_id)

   
if __name__ == "__main__":
    asyncio.run(main())


# # python store_guess.py --guess Hangman --game_master_id 12D3KooWLm5k5URp3AcBySRQk6ubzVPcGyD5WtD1Lox6DSo3SPJG 
# --cluster_id 9e68173f-9c23-4acc-ba81-4f079b639964 
# --userkey /tmp/tmp.KIvtoocja4 --nodekey /tmp/tmp.Tf0zucZg1S --program_id 5CmaQc9FLadgeX88j4vghoVAYzSyPQxEeM7Q9GPLm5xgJn9WdGfrAqhF95MqrM6n2ERgDksHQqraWfLfMTRTf4mm//hangman
