class Course:
    def __init__(self, name, teacher, time,classroom):
        self.name = name
        self.teacher = teacher
        self.time = time
        self.classroom = classroom

    def show_info(self):
        print(f"{self.name} {self.teacher}  {self.time} {self.classroom}")


