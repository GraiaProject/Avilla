# class rings

class ring1:
    def __init__(self):
        print("ring1")
    
    @property
    def ring3(self):
        class inheri:
            def __init_subclass__(cls) -> None:
                print("ring3")
        return inheri

    def ring2(self):
        print("ring2")

def ring4(cls):
    print("ring4")
    return cls

@ring4
class test((m := ring1()).ring3):
    m.ring2()

    def a(self):
        ...