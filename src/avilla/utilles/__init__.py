import random
import string
from typing import Type


def random_string(k=12):
    return "".join(random.choices(string.ascii_letters + string.digits, k=k))
