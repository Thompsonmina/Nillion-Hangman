import subprocess
import os

def execute_python_file(file_path, optional_args=""):

    command = f"python {file_path} {optional_args}"
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    # print(result.stdout)
    if not result.stderr:
        output = result.stdout
        print(output)
        output = {k:v for (k,v) in [x.split(": ") for x in output.splitlines()]}
        return True, output
    else:
        return False, result.stderr

def execute_store_program():
    file_path = "../nillion/nillion_backend/store_program.py"

    # Extract the filename from the file path
    filename = os.path.basename(file_path)
    print(filename)

    base_directory = os.path.dirname(os.path.abspath(__file__))
    base_directory = "/".join(base_directory.split("/")[:-1])

    args = f"--base_dir {base_directory}"
    return execute_python_file(file_path, args)


# execute_store_program()
# exit()
def execute_store_game_attempts(operation, program_id, attempts):

    if operation not in ["store", "retrieve"]: 
        return False, "invalid operation for store game attempts"

    args = f" --operation {operation} --program_id {program_id} --attempts {attempts}"
    return execute_python_file("../nillion/nillion_backend/store_retrieve_game_attempts.py", args)

def execute_perform_computation(provider, guesser, program_id, game_master_store_id):

    args = f" --word_provider_party_id {provider['party_id']} --word_provider_store_id {provider['store_id']} --word_guesser_party_id {guesser['party_id']} --word_guesser_store_id {guesser['store_id']} --program_id {program_id} --game_master_store_id {game_master_store_id}"
    return execute_python_file("../nillion/nillion_backend/compute_game.py", args)

# print(
#     execute_store_game_attempts("store", "3EPkiXLTUNu9ZbsojDmXshzwW9fuA94nKfnWBPa8eQFp25UYek2b8hsR4Hi1EiXhVuvg3A8LUAbdSk1cL6kf8HG6/hangman")
# )
# exit()


# provider =  {"store_id": "8f8dea9a-6ebe-4731-bb21-32d81b5e53cc",
#       "party_id": "12D3KooWLXSj9o3drxQujfuGTic8jVHN4h84M2jjmpD9zJ8n6gZv"
#     }

# provider = {'user_id': '3NdCULQa7sy7Z6CFhYwyRoFxLnKqJ7s1uCGExvoaYH4Jm4VHrwqKpQkLZHtcdvSWTAsBvPLVgxXnhWtrkCPHvxcc', 
#  'party_id': '12D3KooWDYa55n1US9RKvwAL4ZKp3yXcN8cWZfVZP8wmuH6FSfZS', 'party_name': 'word_provider',
#  'store_id': "06006b43-3c97-4e98-af14-1caf61757f6e"}

# player = {'user_id': '4W5WNexjY4vbcek845TJMZryRNxUKB6NchrbCFoPvXyKMoVudAmgQ1nZr2dstSWR9zUHkt9es85LQbiqdvM5g4mP', 
#           'party_id': '12D3KooWMRGdRxTibtranY7vHnyjsoj6VWZq86ayc2SAHEAQKfZx',
#             'party_name': 'word_guesser',
#             'store_id': "d460d39e-105b-4cdd-be54-b7dc1873dacc"}

# program_id = "3EPkiXLTUNu9ZbsojDmXshzwW9fuA94nKfnWBPa8eQFp25UYek2b8hsR4Hi1EiXhVuvg3A8LUAbdSk1cL6kf8HG6/hangman"
# program_id = '3EPkiXLTUNu9ZbsojDmXshzwW9fuA94nKfnWBPa8eQFp25UYek2b8hsR4Hi1EiXhVuvg3A8LUAbdSk1cL6kf8HG6/hangman'
# g_store_id = "fd02e6d4-5f8f-4fb6-baf1-1b9def620000"
# print(execute_perform_computation(provider, player, program_id, g_store_id))
# exit()

def execute_store_guess(guess, cluster_id, game_master_id, program_id, user_key="", node_key=""):

    userkey =  "/tmp/tmp.zsCi49IWAY"
    nodekey =  "/tmp/tmp.Xvo6w20IfO"
    args = f" --guess {guess} --game_master_id {game_master_id} --cluster_id {cluster_id} --userkey {userkey} --nodekey {nodekey} --program_id {program_id}"
    return execute_python_file("../nillion/nillion_backend/store_guess.py", args)


# {'action_id': '7c6ffa4b-aa9b-4b11-b3ac-4297a0fd5f51',
# 'program_id': '2pvWozAEy9QrKX4Yy2Wypr4Adik6HLTTLTcWEwRKtGqWSAjiubb2osmvTGADTbUzgNkPuuMxgyeFzNUdGqDyEnM/hangman',
#  'name': 'hangman', 
#  'game_master_id': '12D3KooWH7zCveCt78GWQRvHdARKeQta8LGLP6varkhWMqerr7hd'})


# game_master_id = "12D3KooWQQPPRdi81JutBxg2zahq5BTZXW7wMmg8kijDRMeL84M7"
# cluster_id = "9e68173f-9c23-4acc-ba81-4f079b639964"
# program_id = "3EPkiXLTUNu9ZbsojDmXshzwW9fuA94nKfnWBPa8eQFp25UYek2b8hsR4Hi1EiXhVuvg3A8LUAbdSk1cL6kf8HG6/hangman"

# print(execute_store_guess("r",cluster_id, game_master_id, program_id))
# exit()

# python store_word_cli.py --word nilli --cluster_id 9e68173f-9c23-4acc-ba81-4f079b639964 --userkey /tmp/tmp.zuC93F5TEj --nodekey /tmp/tmp.ujDAMVvxh9 --game_master_id 12D3KooWQQPPRdi81JutBxg2zahq5BTZXW7wMmg8kijDRMeL84M7 --program_id 3EPkiXLTUNu9ZbsojDmXshzwW9fuA94nKfnWBPa8eQFp25UYek2b8hsR4Hi1EiXhVuvg3A8LUAbdSk1cL6kf8HG6/hangman
# 12D3KooWLXSj9o3drxQujfuGTic8jVHN4h84M2jjmpD9zJ8n6gZv

# 09695554-39ed-45d5-9ee3-76820640183c store
