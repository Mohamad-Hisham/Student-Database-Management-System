from src.student import Student


class Chatbot:
    def __init__(self, database):
        self.database = database

    def text_response(self, message):
        return {
            "type": "text",
            "message": message
        }

    def table_response(self, message, students):
        student_data = []

        for student in students:
            student_data.append(
                {
                    "ID": student.student_id,
                    "Name": student.name,
                    "Age": student.age,
                    "Grade": student.grade
                }
            )

        return {
            "type": "table",
            "message": message,
            "data": student_data
        }

    def respond(self, message, role):
        original_message = message.strip()
        normalized_message = original_message.lower()

        
        if normalized_message in ["hello", "hi", "hey"]:
            return self.text_response(
                "Hello! Ask me a question about the students."
            )

        
        if normalized_message.startswith("add student"):
            if role != "admin":
                return self.text_response(
                    "Only administrators can add students."
                )

            student_details = original_message[
                len("add student"):
            ].strip()

            parts = student_details.split(",", maxsplit=2)

            if len(parts) != 3:
                return self.text_response(
                    "Please use this format:\n\n"
                    "`add student Name, Age, Grade`"
                )

            name = parts[0].strip()
            age_text = parts[1].strip()
            grade = parts[2].strip()

            if not name:
                return self.text_response(
                    "The student's name is required."
                )

            if not age_text.isdigit():
                return self.text_response(
                    "The student's age must be a number."
                )

            age = int(age_text)

            if age < 1 or age > 120:
                return self.text_response(
                    "The student's age must be between 1 and 120."
                )

            if not grade:
                return self.text_response(
                    "The student's grade is required."
                )

            student = Student(
                name=name,
                age=age,
                grade=grade
            )

            student_id = self.database.add_student(student)

            return self.table_response(
                (
                    f"Student added successfully "
                    f"with ID {student_id}."
                ),
                [student]
            )

        
                
        if normalized_message.startswith("update student"):
            if role != "admin":
                return self.text_response(
                    "Only administrators can update students."
                )

            student_details = original_message[
                len("update student"):
            ].strip()

            parts = student_details.split(",", maxsplit=3)

            if len(parts) != 4:
                return self.text_response(
                    "Please use this format:\n\n"
                    "`update student ID, Name, Age, Grade`"
                )

            student_id_text = parts[0].strip()
            name = parts[1].strip()
            age_text = parts[2].strip()
            grade = parts[3].strip()

            if not student_id_text.isdigit():
                return self.text_response(
                    "The student ID must be a number."
                )

            if not name:
                return self.text_response(
                    "The student's name is required."
                )

            if not age_text.isdigit():
                return self.text_response(
                    "The student's age must be a number."
                )

            age = int(age_text)

            if age < 1 or age > 120:
                return self.text_response(
                    "The student's age must be between 1 and 120."
                )

            if not grade:
                return self.text_response(
                    "The student's grade is required."
                )

            student_id = int(student_id_text)

            student = self.database.get_student_by_id(
                student_id
            )

            if student is None:
                return self.text_response(
                    f"No student was found with ID {student_id}."
                )

            student.update(
                name=name,
                age=age,
                grade=grade
            )

            updated = self.database.update_student(
                student
            )

            if not updated:
                return self.text_response(
                    "The student could not be updated."
                )

            return self.table_response(
                f"Student {student_id} was updated successfully.",
                [student]
            )

                
        if normalized_message.startswith("delete student"):
            if role != "admin":
                return self.text_response(
                    "Only administrators can delete students."
                )

            student_id_text = original_message[
                len("delete student"):
            ].strip()

            if not student_id_text.isdigit():
                return self.text_response(
                    "Please use this format:\n\n"
                    "`delete student ID`"
                )

            student_id = int(student_id_text)

            student = self.database.get_student_by_id(
                student_id
            )

            if student is None:
                return self.text_response(
                    f"No student was found with ID {student_id}."
                )

            deleted = self.database.delete_student(
                student_id
            )

            if not deleted:
                return self.text_response(
                    "The student could not be deleted."
                )

            return self.text_response(
                (
                    f"Student {student.name} with ID "
                    f"{student_id} was deleted successfully."
                )
            )
        
        if "how many students" in normalized_message:
            students = self.database.get_all_students()

            return self.text_response(
                f"There are {len(students)} students in the database."
            )



                
        if normalized_message.startswith("find student"):
            student_name = original_message[
                len("find student"):
            ].strip()

            if not student_name:
                return self.text_response(
                    "Please use this format:\n\n"
                    "`find student Name`"
                )

            students = self.database.get_students_by_name(
                student_name
            )

            if len(students) == 0:
                return self.text_response(
                    f"No students were found matching "
                    f"the name '{student_name}'."
                )

            return self.table_response(
                (
                    f"I found {len(students)} student(s) "
                    f"matching '{student_name}':"
                ),
                students
            )



                
        grade_command = "show students with grade"

        if normalized_message.startswith(grade_command):
            grade = original_message[
                len(grade_command):
            ].strip()

            if not grade:
                return self.text_response(
                    "Please use this format:\n\n"
                    "`show students with grade A`"
                )

            students = self.database.get_students_by_grade(
                grade
            )

            if len(students) == 0:
                return self.text_response(
                    f"No students were found with grade '{grade}'."
                )

            return self.table_response(
                (
                    f"I found {len(students)} student(s) "
                    f"with grade '{grade}':"
                ),
                students
            )
        
        if normalized_message.startswith("student id"):
            student_id_text = normalized_message.replace(
                "student id",
                "",
                1
            ).strip()

            if not student_id_text.isdigit():
                return self.text_response(
                    "Please enter a valid student ID."
                )

            student_id = int(student_id_text)

            student = self.database.get_student_by_id(
                student_id
            )

            if student is None:
                return self.text_response(
                    "Student not found."
                )

            return self.table_response(
                f"Here is the student with ID {student_id}:",
                [student]
            )

        
        if normalized_message in [
            "show all students",
            "list all students",
            "all students"
        ]:
            students = self.database.get_all_students()

            if len(students) == 0:
                return self.text_response(
                    "No students were found in the database."
                )

            return self.table_response(
                f"I found {len(students)} students:",
                students
            )

        return self.text_response(
            "Sorry, I do not understand that command yet."
        )