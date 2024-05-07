from nada_dsl import *


def nada_main():
    party1 = Party(name="Party1")
    my_array_1 = Array(SecretInteger(Input(name="my_array_1", party=party1)), size=5)
    my_int = SecretInteger(Input(name="my_int", party=party1))

    @nada_fn
    def inc(a: SecretInteger) -> SecretInteger:
        return (a < Integer(26)).if_else(Integer(1), Integer(0))

    @nada_fn
    def check_valid(acc: SecretInteger, a: SecretInteger) -> SecretInteger:
        return (acc <= Integer(0)).if_else(Integer(0), 
                    (a < Integer(26)).if_else(Integer(1), Integer(0)))
        
    



    out = Output(inc(my_int), "out_1", party1)

    check_result = my_array_1.reduce(check_valid, Integer(1))
    out2 = Output(check_result, "valid_check", party1)

    return [out, out2]
