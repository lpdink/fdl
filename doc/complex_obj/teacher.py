from fdl import register_as


@register_as("Student")
class Student:
    def __init__(self, name) -> None:
        self.name = name


@register_as("Teacher")
class Teacher:
    def __init__(self, students: list[Student]) -> None:
        self.students = students

    def call_name(self):
        for student in self.students:
            print(student.name)
