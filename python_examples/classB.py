"""example class"""

from classA import A


class B:
    """Test class B"""

    def __init__(self):
        self.a = A()

    def do_b(self):
        """use a to do something"""
        return self.a.do_a()
