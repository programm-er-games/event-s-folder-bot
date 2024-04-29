import random
import string


def rand_str(length: int):
    result = ''.join(random.choices(string.ascii_lowercase, k=length))
    return result
