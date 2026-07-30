class Chatbot:
    def __init__(self, database):
        self.database = database


    def respond(self, message):
        message = message.strip().lower()

        if message in ["hello", "hi", "hey"]:
            return "Hello! Ask me a question about the students."

        if "how many students" in message:
            students = self.database.get_all_students()
            return f"Number of students: {len(students)}"

        if message.startswith("student id"):
            student_id_text = message.replace("student id", "").strip()

            if not student_id_text.isdigit():
                return "Please enter a valid student ID."

            student_id = int(student_id_text)
            student = self.database.get_student_by_id(student_id)

            if student is None:
                return "Student not found."

            return (
                f"Student ID: {student.student_id}\n"
                f"Name: {student.name}\n"
                f"Age: {student.age}\n"
                f"Grade: {student.grade}"
            )


        if message in ["show all students", "list all students", "all students"]:
            students = self.database.get_all_students()

            if len(students) == 0:
                return "No students found."

            response = "Students:\n"

            for student in students:
                response += (
                    f"\nID: {student.student_id}\n"
                    f"Name: {student.name}\n"
                    f"Age: {student.age}\n"
                    f"Grade: {student.grade}\n"
                )

            return response        

        return "Sorry, I do not understand that question yet."
        