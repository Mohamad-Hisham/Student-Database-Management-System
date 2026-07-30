import json
from hashlib import sha256
from pathlib import Path

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

    if st.sidebar.button(
        "Logout",
        use_container_width=True
    ):
        logout()
        st.rerun()

    st.success(
        f"Welcome, {st.session_state.username}!"
    )

if st.session_state.role == "admin":
    st.header("Admin Dashboard")
    st.subheader("Add Student")

    with st.form("add_student_form"):
        name = st.text_input("Student Name")

        age = st.number_input(
            "Student Age",
            min_value=1,
            max_value=120,
            step=1
        )

        grade = st.text_input("Student Grade")

        add_student_button = st.form_submit_button(
            "Add Student"
        )

    if add_student_button:
        name = name.strip()
        grade = grade.strip()

        if not name or not grade:
            st.error(
                "Student name, age, and grade are required."
            )

        else:
            try:
                student = Student(
                    name=name,
                    age=int(age),
                    grade=grade
                )

                student_id = database.add_student(student)

                st.success(
                    f"Student added successfully with ID: {student_id}"
                )

            except ValueError as error:
                st.error(str(error))

    elif st.session_state.role == "user":
        st.header("User Dashboard")
        st.info(
            "The student chatbot will be added here."
        )