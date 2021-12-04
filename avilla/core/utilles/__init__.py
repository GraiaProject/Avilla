import random
import string


def random_string(k: int = 12):
    return "".join(random.choices(string.ascii_letters + string.digits, k=k))


def as_async(func):
    async def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
