import random
import string


def random_string(k=12):
    return "".join(random.choices(string.ascii_letters + string.digits, k=k))
