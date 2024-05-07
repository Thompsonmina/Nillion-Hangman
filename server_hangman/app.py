import os

from generate_code import generate_hangman_code
from executor import execute_store_program, execute_store_game_attempts, execute_store_guess, execute_perform_computation
from utils import dump_json_safe, load_json_safe

from dotenv import load_dotenv
load_dotenv()


from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

GAMES_PATH = "db/games.json"
CLUSTER_ID = os.getenv("NILLION_CLUSTER_ID")
GAME_MASTER_USER_ID = "3EPkiXLTUNu9ZbsojDmXshzwW9fuA94nKfnWBPa8eQFp25UYek2b8hsR4Hi1EiXhVuvg3A8LUAbdSk1cL6kf8HG6"


@app.route("/")
def index():
    return render_template('index.html')

@app.route('/create-game')
def start_game():
    store_code = file_to_string("../nillion/nillion_backend/store_word_cli.py")
    hangman_code = generate_hangman_code(8)

    wordstore_progam = "store_word_cli.py"
    program_store = "hangman.py"

    return render_template('create_game.html', store_code=store_code,
                    wordstore_program_name=wordstore_progam, 
                    program_store_program_name=program_store,
                    hangman_code=hangman_code)

@app.route('/games/<game_name>')
def show_game(game_name):
    games = load_json_safe(GAMES_PATH)
    program_id = GAME_MASTER_USER_ID + "/" + game_name
    game = games.get(program_id)


    if not game:
        return render_template("error.html", error_message="game does not exist")

    return render_template('game.html', game_num=game["number"],
                creator=game["creator"]["name"],
                status=game["status"]
    )

# ideally this should be happening on the client, alas couldnt figure out how to get the js client
# to work on time

@app.route('/store-letter-for-user/<game_name>/<name>', methods=['POST'])
def store_letter_for_user(game_name, name):

    program_id = GAME_MASTER_USER_ID + "/" + game_name
    data = request.get_json()

    guess = data.get("guess")

    games = load_json_safe(GAMES_PATH)
    game = games.get(program_id)
    if not game:
        return jsonify({"error_message": "A game with the provided program id does not currently exist"}), 404
    
    if game["player"]["name"] != name:
        return jsonify({"error_message": "Player is not a participant in this game"})
    
    g_p_id = game["gamemaster"]["party_id"]

    success, result = execute_store_guess(guess, CLUSTER_ID, g_p_id, program_id, user_key="", node_key="")
    
    if success:

        print(result)
        return jsonify(result)

    return jsonify({"error_message": "Something Went Wrong"})

@app.route('/perform-hangman-computation/<game_name>/<name>', methods=['POST'])
def perform_hangman_computation(game_name, name):

    program_id = GAME_MASTER_USER_ID + "/" + game_name
    data = request.get_json()

    games = load_json_safe(GAMES_PATH)
    game = games.get(program_id)
    if not game:
        return jsonify({"error_message": "A game with the provided program id does not currently exist"}), 404
    
    if game["player"]["name"] != name:
        return jsonify({"error_message": "Player is not a participant in this game"})

    if game.get("status") == "concluded":
        return jsonify({"error_message": "Game ahs already ended"})
    

    store_id = data.get("letter_store_id")
    party_id = data.get("player_party_id")
    print(store_id, party_id, "check")


    provider = {'party_id': game["creator"]["party_id"],
        'store_id': game["creator"]["store_id"]}

    player = {'user_id': '4W5WNexjY4vbcek845TJMZryRNxUKB6NchrbCFoPvXyKMoVudAmgQ1nZr2dstSWR9zUHkt9es85LQbiqdvM5g4mP', 
            'party_id': '12D3KooWMRGdRxTibtranY7vHnyjsoj6VWZq86ayc2SAHEAQKfZx',
                'party_name': 'word_guesser',
                'store_id': "d460d39e-105b-4cdd-be54-b7dc1873dacc"}

    # program_id = program_id


    
    g_store_id = game["gamemaster"]["store_id"]

    success, result = execute_perform_computation(provider, player, program_id, g_store_id)


    if success:
        game["guessed"] = str(int(game["guessed"]) + int(result["slots_guessed"]))
        attempts_left = result["attempts_left"] if int(result["attempts_left"]) > 0 else -1
        print(attempts_left, "yeah")
        success, store = execute_store_game_attempts("store", program_id, attempts_left)
        
        if success:
            print(success, store)
            game["attempts_left"] = result["attempts_left"]
            game["gamemaster"]["store_id"] = store["game_master_storeid"]
            games[program_id] = game


            win = int(game["guessed"]) >= int(game["word_length"])
            gameover = int(game["attempts_left"]) <= 0 and not win

            if win or gameover:
                game["status"] = "concluded"

            dump_json_safe(games, GAMES_PATH)

            return jsonify({"slots_guessed": game["guessed"],
                "slots_left": int(game["word_length"]) - int(game["guessed"]),
                "attempts_left": int(game["attempts_left"]), 
                "won": win, "gameover":gameover}
                )
        
        print(store)
        return jsonify({"error_message": "Error Unable to store game state"})

    print(result)
    print("got into route")


@app.route('/games/<game_name>/<name>')
def play_game(game_name, name):
    program_id = GAME_MASTER_USER_ID + "/" + game_name

    games = load_json_safe(GAMES_PATH)
    game = games.get(program_id)
    if not game:
        return jsonify({"error_message": "A game with the provided program id does not currently exist"}), 404
    
    if game["player"]["name"] != name:
        return render_template("error.html")
    
    thingy = "?" * int(game["word_length"])
    attempts = game["attempts_left"]

    return render_template("actual_game.html", word_thingy=thingy,
                           slots_filled=0, slots_left=attempts)


@app.route('/view-games')
def view_games():
    return render_template('view_games.html')  # Page to view games

@app.route("/game-actions/<game_name>", methods=['POST'])
def game_actions(game_name):
    program_id = GAME_MASTER_USER_ID + "/" + game_name
    data = request.get_json()
    action = data.get("action")

    if action == "join":

        name = data.get("name")
        games = load_json_safe(GAMES_PATH)
        game = games.get(program_id)
        if not game:
            return jsonify({"error_message": "A game with the provided program id does not currently exist"}), 404
        
        game["status"] = "in progress"
        game["player"] = {"name": name}
        game["guessed"] = 0

        games[program_id] = game
        dump_json_safe(games, GAMES_PATH)
        return jsonify({"status":"in progress" , "attempts_left":game["attempts_left"]})
    

@app.route('/test')
def test():
    return render_template('test.html') 

@app.route("/store-hangman-program", methods=['POST'])
def store_hanggame():
    # json is a temporary measure, idealy we would want to persist this in an actual db or on a blockchain somewhere
    
    data = request.get_json()
    action = data.get("action")

    if action == "start_creation":
        word_length = data.get('wordLength')
        creator_name = data.get('creatorName')    
        hangman_code = generate_hangman_code(word_length)
        success, result = execute_store_program()
        print("huh")
        if not success:
            print(result)
            return jsonify({"error_message": "something went wrong will trying to store program"}), 500
        else:
            success, attempt = execute_store_game_attempts("store", result["program_id"], 10)
            if not success:
                return jsonify({"error_message": "something went wrong while trying to stor game state"}), 500

            print(attempt)

            games = load_json_safe(GAMES_PATH) 
            games[result["program_id"]] = {
                "creator": {"name": creator_name},
                "status": "created",
                "attempts_left": "10", 
                "gamemaster": {"party_id": result["game_master_party_id"],
                                "store_id":attempt["game_master_storeid"]},
                "word_length":word_length
            }   

            games[result["program_id"]]["number"] = len(games)

            dump_json_safe(games, GAMES_PATH)

            return jsonify({"program_id": result["program_id"], "game_master_party_id": result["game_master_party_id"]})
    
    elif action == "finalise_creation":
        game_name = data.get("game_name")
        program_id = GAME_MASTER_USER_ID + "/" + game_name
        creator_party_id = data.get("creator_party_id")
        creator_store_id = data.get("creator_store_id")

        games = load_json_safe(GAMES_PATH)
        game = games.get(program_id)
        print(games)
        if not game:
            return jsonify({"error_message": "A game with the provided program id does not currently exist"}), 404
        
        game["creator"]["store_id"] = creator_store_id
        game["creator"]["party_id"] = creator_party_id

        games[program_id]
        dump_json_safe(games, GAMES_PATH)
        return jsonify({"program_id": program_id, "game_name":game_name})

    else:
        return jsonify({"error_message": "Invalid action"}), 400

def file_to_string(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return str(e)


# next store attempts functionality
# get attempts function

# list games, enroll, play a round

if __name__ == "__main__":
    app.run(debug=True)
