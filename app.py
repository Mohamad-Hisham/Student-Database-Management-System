import json
from hashlib import sha256
from pathlib import Path
import csv

import streamlit as st

from src.database import Database
from src.chatbot import Chatbot
from src.student import Student
BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / "data" / "users.json"
CREDENTIALS_FILE = BASE_DIR / "data" / "credentials.json"

def hash_password(password):
    return sha256(password.encode("utf-8")).hexdigest()


def load_users():
    if not USERS_FILE.exists() or USERS_FILE.stat().st_size == 0:
        return {}

    with USERS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_admin_credentials():
    if (
        not CREDENTIALS_FILE.exists()
        or CREDENTIALS_FILE.stat().st_size == 0
    ):
        return {}

    with CREDENTIALS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)
    

def save_users(users):
    with USERS_FILE.open("w", encoding="utf-8") as file:
        json.dump(users, file, indent=4)


def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I am the Student Database Chatbot. "
                "Ask me a question about the students."
            )
        }
    ]


st.set_page_config(
    page_title="Student Database Management System",
    page_icon="🎓",
    layout="centered"
)


database = Database()
chatbot = Chatbot(database)


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "role" not in st.session_state:
    st.session_state.role = None


if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I am the Student Database Chatbot. "
                "Ask me a question about the students."
            )
        }
    ]

st.title("🎓 Student Database Management System")


if not st.session_state.logged_in:
    page = st.radio(
        "Choose a page",
        ["Login", "Register"],
        horizontal=True
    )

    if page == "Login":
        st.subheader("Login")

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input(
                "Password",
                type="password"
            )

            login_button = st.form_submit_button("Login")

        if login_button:
            username = username.strip()

            if not username or not password:
                st.error("Username and password are required.")

            else:
                admins = load_admin_credentials()
                users = load_users()

                entered_password_hash = hash_password(password)
                admin = admins.get("admin", {})

                if (
                    username == admin.get("username")
                    and entered_password_hash == admin.get("password")
                ):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = "admin"

                    st.rerun()

                elif (
                    username in users
                    and entered_password_hash
                    == users[username]["password"]
                ):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = "user"

                    st.rerun()

                else:
                    st.error("Invalid username or password.")

    elif page == "Register":
        st.subheader("Register")

        with st.form("registration_form"):
            username = st.text_input("Username")
            password = st.text_input(
                "Password",
                type="password"
            )
            confirm_password = st.text_input(
                "Confirm Password",
                type="password"
            )

            register_button = st.form_submit_button("Register")

        if register_button:
            username = username.strip()
            users = load_users()

            if not username or not password or not confirm_password:
                st.error("All fields are required.")

            elif password != confirm_password:
                st.error("Passwords do not match.")

            elif username in users:
                st.error("Username already exists.")

            else:
                users[username] = {
                    "password": hash_password(password),
                    "role": "user"
                }

                save_users(users)

                st.success(
                    "Registration successful! You can now log in."
                )

else:
    st.sidebar.success(
        f"Logged in as: {st.session_state.username}"
    )

    st.sidebar.write(
        f"Role: {st.session_state.role}"
    )

    st.sidebar.divider()

    st.sidebar.subheader("Example Messages")

    st.sidebar.write("• Hello")
    st.sidebar.write("• How many students?")
    st.sidebar.write("• Show all students")
    st.sidebar.write("• Student ID 1")
    st.sidebar.write("• Find student Ahmed")
    st.sidebar.write("• Show students with grade A")
    if st.session_state.role == "admin":
        st.sidebar.write(
            "• Add student Ahmed Mohamed, 20, A"
        )
        st.sidebar.write(
            "• Update student 1, Ahmed Mohamed, 21, B"
        )
        st.sidebar.write(
            "• Delete student 1"
        )

    st.sidebar.divider()

    if st.sidebar.button(
        "Logout",
        use_container_width=True
    ):
        logout()
        st.rerun()

    st.header("🤖 Student Database Chatbot")

    st.caption(
        "Type a message below to interact with the student database."
    )

    # CSV bulk upload — admins only
    if st.session_state.role == "admin":
        with st.sidebar.expander(" Bulk Upload Students"):
            uploaded_file = st.file_uploader(
                "Upload a CSV file",
                type=["csv"],
                key="students_csv"
            )

            if uploaded_file is not None:
                if st.button(
                    "Import Students",
                    key="import_students_button",
                    use_container_width=True
                ):
                    try:
                        file_content = uploaded_file.getvalue().decode(
                            "utf-8-sig"
                        )

                        csv_rows = csv.DictReader(
                            file_content.splitlines()
                        )

                        required_columns = {
                            "name",
                            "age",
                            "grade"
                        }

                        if csv_rows.fieldnames is None:
                            st.error("The CSV file is empty.")

                        elif not required_columns.issubset(
                            set(csv_rows.fieldnames)
                        ):
                            st.error(
                                "The CSV must contain these columns: "
                                "name, age, grade."
                            )

                        else:
                            students = []

                            for row_number, row in enumerate(
                                csv_rows,
                                start=2
                            ):
                                name = row["name"].strip()
                                age_text = row["age"].strip()
                                grade = row["grade"].strip()

                                if not name:
                                    raise ValueError(
                                        f"Name is missing in row "
                                        f"{row_number}."
                                    )

                                if not age_text.isdigit():
                                    raise ValueError(
                                        f"Age must be a number in row "
                                        f"{row_number}."
                                    )

                                age = int(age_text)

                                if age < 1 or age > 120:
                                    raise ValueError(
                                        f"Invalid age in row "
                                        f"{row_number}."
                                    )

                                if not grade:
                                    raise ValueError(
                                        f"Grade is missing in row "
                                        f"{row_number}."
                                    )

                                students.append(
                                    Student(
                                        name=name,
                                        age=age,
                                        grade=grade
                                    )
                                )

                            if len(students) == 0:
                                st.error(
                                    "The CSV contains no student records."
                                )

                            else:
                                added_count = database.add_students(
                                    students
                                )

                                st.success(
                                    f"{added_count} students were "
                                    f"imported successfully."
                                )

                    except UnicodeDecodeError:
                        st.error(
                            "The CSV file must use UTF-8 encoding."
                        )

                    except ValueError as error:
                        st.error(str(error))

                    except Exception as error:
                        st.error(
                            f"CSV import failed: {error}"
                        )

    # Display all previous chat messages.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("type") == "table":
                st.dataframe(
                    message["data"],
                    use_container_width=True,
                    hide_index=True
                )
    # This must be outside the for loop.
    user_message = st.chat_input(
        "Ask something about the students...",
        key="student_chat_input"
    )

    if user_message:
        # Save and display the user's message.
        user_chat_message = {
            "role": "user",
            "content": user_message
        }

        st.session_state.messages.append(
            user_chat_message
        )

        with st.chat_message("user"):
            st.markdown(user_message)

        # Send the message to the chatbot.
        chatbot_response = chatbot.respond(
            user_message,
            st.session_state.role
        )

        # Prepare the chatbot message.
        assistant_message = {
            "role": "assistant",
            "content": chatbot_response["message"],
            "type": chatbot_response["type"]
        }

        if chatbot_response["type"] == "table":
            assistant_message["data"] = (
                chatbot_response["data"]
            )

        # Save every response, whether text or table.
        st.session_state.messages.append(
            assistant_message
        )

        # Display the chatbot response.
        with st.chat_message("assistant"):
            st.markdown(
                chatbot_response["message"]
            )

            if chatbot_response["type"] == "table":
                st.dataframe(
                    chatbot_response["data"],
                    use_container_width=True,
                    hide_index=True
                )