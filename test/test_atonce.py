# 测试原地构造对象的结果。
from fdl import register

@register
class Teacher:
    def __init__(self, students:list) -> None:
        self.students = students

    def call(self):
        # breakpoint()
        for s in self.students:
            s.call()

@register
class Student:
    def __init__(self, name) -> None:
        self.name = name
        self.id = "not set"

    def call(self):
        print(self.name, self.id)

    def set_id(self, id):
        self.id = id
        return self