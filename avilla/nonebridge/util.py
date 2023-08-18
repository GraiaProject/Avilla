import inspect


def print_tb():
    stacks = inspect.stack()
    print("inspecting")
    for i in stacks:
        print(f"  at {i.frame.f_globals['__name__']}:{i.lineno}")
