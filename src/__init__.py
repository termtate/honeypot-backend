from injector import inject, Injector, singleton

@singleton
class A:
    pass


class B:
    @inject
    def __init__(self, a: A) -> None:
        print(a)


injector = Injector()

b1 = injector.get(B)
b2 = injector.get(B)

print(b1 is b2)
