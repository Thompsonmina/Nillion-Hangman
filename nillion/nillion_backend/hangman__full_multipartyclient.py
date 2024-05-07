import asyncio
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

Program = namedtuple("Program", ["action_id", "program_id"])

async def store_program(cluster_id, client, user_id, program_name):
    
    program_mir_path=f"../programs-compiled/{program_name}.nada.bin"

    # store program
    action_id = await client.store_program(
        cluster_id, program_name, program_mir_path
    )

    program_id=f"{user_id}/{program_name}"

    print('Stored program. action_id:', action_id)
    print('Stored program_id:', program_id)

    return Program(action_id, program_id)


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

    print(f"\n🎉Party {client_dict['party_id']} stored secret  at store id: {store_id}")
    print(f"\n🎉Compute permission on the secret granted to user_id: {delegate_user_id}")


    return store_id

async def main():
    cluster_id = os.getenv("NILLION_CLUSTER_ID")

    game_master_client = create_client(chinedu["userkey_file"], chinedu["nodekey_file"])
    game_master = {"user_id":game_master_client.user_id(), "party_id":game_master_client.party_id(),
                   "party_name":"game_master"}


    #store program
    program_name="hangman"
    program = await store_program(cluster_id, game_master_client, game_master["user_id"], program_name)
    print(program)

    stored_secret_array = nillion.Secrets(
        {  
            "attempts_left": nillion.SecretInteger(7)
            }
        )
    
    secret_bindings = nillion.ProgramBindings(program.program_id)
    secret_bindings.add_input_party(game_master["party_name"], game_master["party_id"])

    # Store a secret array
    game_master_store_id = await game_master_client.store_secrets(
        cluster_id, secret_bindings, stored_secret_array, None
    )

    print(game_master)
    print(game_master_store_id, "g_s_id")

    word_provider_client = create_client(adaobi["userkey_file"], adaobi["nodekey_file"])
    word_provider = {"user_id":word_provider_client.user_id(), "party_id":word_provider_client.party_id(),
                   "party_name":"word_provider"}
    

    secret_array= nillion.SecretArray([
        nillion.SecretInteger(19),
        nillion.SecretInteger(5),
        nillion.SecretInteger(22),
        nillion.SecretInteger(5),
        nillion.SecretInteger(14),
    ])

    secret_array = nillion.Secrets(
        {   "word": secret_array }
    )

    print("adaobiiiiii")

    print(cluster_id, "cluster_id")
    print(adaobi["userkey_file"], "ada_u")
    print(adaobi["nodekey_file"], "ada_n")


    word_provider_store_id = await delegate_permission_and_store_secret(cluster_id, word_provider_client, word_provider,
                            secret_array, game_master["user_id"], program.program_id)

    print(word_provider, "PROVIDER")
    print(word_provider_store_id)
    
    word_guesser_client = create_client(bisi["userkey_file"], bisi["nodekey_file"])
    word_guesser = {"user_id":word_guesser_client.user_id(), "party_id":word_guesser_client.party_id(),
                   "party_name":"word_guesser"}


    secret_guess = nillion.Secrets(
        {
            "guessed_letter": nillion.SecretInteger(5),
        }
    )
    word_guesser_store_id = await delegate_permission_and_store_secret(cluster_id, word_guesser_client, word_guesser,
                            secret_guess, game_master["user_id"], program.program_id)


    print(word_guesser, "GUESSER")
    print(word_guesser_store_id)

    # _____________________________________________________


    # Bind the parties in the computation to the client to set input and output parties
    compute_bindings = nillion.ProgramBindings(program.program_id)
    compute_bindings.add_input_party(game_master["party_name"], game_master["party_id"])
    compute_bindings.add_input_party(word_provider["party_name"], word_provider["party_id"])
    compute_bindings.add_input_party(word_guesser["party_name"], word_guesser["party_id"])
    compute_bindings.add_output_party(game_master["party_name"], game_master["party_id"])

    print(f"Computing using program {program.program_id}")
    print(f"Use secret store_ids")

    computation_time_secrets = nillion.Secrets({})
    # nillion.Secrets({"my_int1": nillion.SecretInteger(5)})
    
    # Compute on the secret
    compute_id = await game_master_client.compute(
        cluster_id,
        compute_bindings,
        [game_master_store_id, word_provider_store_id, word_guesser_store_id],
        computation_time_secrets,
        nillion.PublicVariables({}),
    )

    # Print compute result
    print(f"The computation was sent to the network. compute_id: {compute_id}")
    while True:
        compute_event = await game_master_client.next_compute_event()
        if isinstance(compute_event, nillion.ComputeFinishedEvent):
            print(f"✅  Compute complete for compute_id {compute_event.uuid}")
            print(f"🖥️  The result is {compute_event.result.value}")
            return compute_event.result.value
    
if __name__ == "__main__":
    asyncio.run(main())

@pytest.mark.asyncio
async def test_main():
    result = await main()
    assert result == {'reduce.addition': 15}
