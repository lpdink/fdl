from fdl import register_as


@register_as("SayMsgClass")
class SayMsg:
    def __init__(self, msg):
        self.msg = msg

    def say_msg(self):
        print("Hey here!", self.msg)
