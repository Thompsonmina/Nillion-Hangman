from nada_dsl import *


def nada_main():
    game_master = Party(name="game_master")
    word_provider = Party(name="word_provider")
    word_guesser = Party(name="word_guesser")
    word = Array(SecretInteger(Input(name="word", party=word_provider)), size=5)
    guessed_letter = SecretInteger(Input(name="guessed_letter", party=word_guesser))
    attempts_left = SecretInteger(Input(name="attempts_left", party=game_master))

    @nada_fn
    def identify(a: SecretInteger) -> SecretInteger:
        return (a.public_equals(guessed_letter)).if_else(Integer(1), Integer(0))
    
    
    @nada_fn
    def sum(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a + b


    # this should have allowed me get the postions, when a letter matched multiple times in a word 
    # The positions would been teased out using modular arithmetic when the result was gotten on the client side
    # unfortunately the below code errors out even though it should work
    # @nada_fn
    # def positions(a: SecretInteger, b: SecretInteger) -> SecretInteger:
    #     return (b.public_equals(guessed_letter)).if_else((a * Integer(10)) + Integer(1), a + Integer(1))
    
    # pos_score = word.reduce(positions, Integer(1))
    # p_score = Output(pos_score, "hmm", game_master)


    new_array = word.map(identify)
    slots_guessed = new_array.reduce(sum, Integer(0))

    new_remaining_attempts = attempts_left - Integer(1)
    remaining_slots_o = Output(new_remaining_attempts, "attempts_left", game_master)
    guess = Output(slots_guessed, "slots_guessed_in_attempt", game_master)

    # out = Output(num, "out", game_master)

    return [guess, remaining_slots_o]
