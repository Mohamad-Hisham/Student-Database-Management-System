import sqlite3
from pathlib import Path
from src.student import Student


class Database:
    def __init__(self):
        
        project_root = Path(__file__).resolve().parent.parent
        data_folder = project_root / "data"
        data_folder.mkdir(exist_ok=True)
        self.database_path = data_folder / "student.db"
        self.initialize_database()

    def initialize_database(self):
        """Create the students table if it does not already exist."""

        try:
            with sqlite3.connect(self.database_path) as connection:
                cursor = connection.cursor()

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        age INTEGER NOT NULL,
                        grade TEXT NOT NULL
                    )
                    """
                )

                connection.commit()

        except sqlite3.Error as error:
            print(f"Database initialization error: {error}")

    def add_student(self, student):
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO students (name, age, grade)
                VALUES (?, ?, ?)
                """,
                (student.name, student.age, student.grade),
            )

            connection.commit()

            student.student_id = cursor.lastrowid

            return student.student_id

    def add_students(self, students):
        student_values = []

        for student in students:
            student_values.append(
                (
                    student.name,
                    student.age,
                    student.grade
                )
            )

        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()

            cursor.executemany(
                """
                INSERT INTO students (name, age, grade)
                VALUES (?, ?, ?)
                """,
                student_values
            )

            connection.commit()

        return len(student_values)
        
    def get_all_students(self):
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT id, name, age, grade
                FROM students
                """
            )

            rows = cursor.fetchall()

        students = []

        for row in rows:
            student = Student(
                name=row[1],
                age=row[2],
                grade=row[3],
                student_id=row[0],
            )

            students.append(student)

        return students                



    def get_student_by_id(self, student_id):
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT id, name, age, grade
                FROM students
                WHERE id = ?
                """,
                (student_id,)
            )

            row = cursor.fetchone()

        if row is None:
            return None

        student = Student(
            name=row[1],
            age=row[2],
            grade=row[3],
            student_id=row[0]
        )

        return student   

     
    def update_student(self, student):
        if student.student_id is None:
            return False

        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE students
                SET name = ?, age = ?, grade = ?
                WHERE id = ?
                """,
                (
                    student.name,
                    student.age,
                    student.grade,
                    student.student_id
                )
            )

            return cursor.rowcount > 0    


    def delete_student(self, student_id):
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE FROM students
                WHERE id = ?
                """,
                (student_id,)
            )

            return cursor.rowcount > 0        

    def get_students_by_name(self, name):
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT id, name, age, grade
                FROM students
                WHERE name LIKE ? COLLATE NOCASE
                """,
                (f"%{name}%",)
            )

            rows = cursor.fetchall()

        students = []

        for row in rows:
            student = Student(
                name=row[1],
                age=row[2],
                grade=row[3],
                student_id=row[0]
            )

            students.append(student)

        return students


    def get_students_by_grade(self, grade):
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT id, name, age, grade
                FROM students
                WHERE grade = ? COLLATE NOCASE
                """,
                (grade,)
            )

            rows = cursor.fetchall()

        students = []

        for row in rows:
            student = Student(
                name=row[1],
                age=row[2],
                grade=row[3],
                student_id=row[0]
            )

            students.append(student)

        return students