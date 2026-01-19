from classA import A
class B:
    def __init__(self):
        self.a = A()
    def do_b(self):
        return self.a.do_a()