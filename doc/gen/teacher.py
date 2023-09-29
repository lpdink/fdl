from fdl import register_as


@register_as("Student")
class Student:
    def __init__(
        self,
        name,
        student_id: int,
        phone: str,
        age: int = 18,
        school_name: str = "Hope Primary School",
        class_number: int = 2,
    ) -> None:
        self.name = name
        self.student_id = student_id
        self.phone = phone
        self.age = age
        self.school_name = school_name
        self.class_number = class_number

    def call_self(self):
        print(
            f"{self.name}, {self.student_id}, {self.phone},"
            f" {self.age},{self.school_name},{self.class_number}"
        )


@register_as("Teacher")
class Teacher:
    def __init__(self, students: list[Student]) -> None:
        self.students = students

    def call_name(self):
        for student in self.students:
            student.call_self()
