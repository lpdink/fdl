from fdl.factory import register


@register
class TestNode:
    def __init__(self, msg) -> None:
        self.msg = msg

    def hello(self):
        print(f"hello {self.msg}!")
