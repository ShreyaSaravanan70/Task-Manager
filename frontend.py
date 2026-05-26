import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Task Manager")

# ---------------- SESSION ----------------

if "token" not in st.session_state:
    st.session_state.token = None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# ---------------- REGISTER ----------------

def register_page():

    st.title("Register")

    name = st.text_input("Name")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input(
    "Create Password",
    type="password",
    key="register_password"
)
    if st.button("Register"):

        payload = {
            "name": name,
            "username": username,
            "password": password,
            "email": email
        }

        response = requests.post(
            f"{BASE_URL}/user/register",
            json=payload
        )

        if response.status_code == 201:
            st.success("Registration Successful")

        else:
            st.error(response.json()["detail"])


# ---------------- LOGIN ----------------

def login_page():

    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input(
    "Password",
    type="password",
    key="login_password"
)
    if st.button("Login"):

        payload = {
            "username": username,
            "password": password
        }

        response = requests.post(
            f"{BASE_URL}/user/login",
            json=payload
        )

        data = response.json()

        if response.status_code == 202:

            st.session_state.token = data["token"]
            st.session_state.logged_in = True

            st.success("Login Successful")
            st.rerun()

        else:
            st.error(data["detail"])


# ---------------- ADD TASK ----------------

def add_task():

    st.header("Add Task")

    title = st.text_input("Task Title")
    description = st.text_area("Task Description")
    is_completed = st.checkbox("Completed")

    if st.button("Create Task"):

        payload = {
            "title": title,
            "description": description,
            "is_completed": is_completed
        }

        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        response = requests.post(
            f"{BASE_URL}/tasks/create",
            json=payload,
            headers=headers
        )

        if response.status_code == 201:
            st.success("Task Created Successfully")
            st.write(response.json())

        else:
            st.error(response.json())


# ---------------- VIEW TASKS ----------------

def view_tasks():

    st.header("All Tasks")

    headers = {
        "Authorization": f"Bearer {st.session_state.token}"
    }

    response = requests.get(
        f"{BASE_URL}/tasks/all_tasks",
        headers=headers
    )

    if response.status_code == 200:

        tasks = response.json()

        if len(tasks) == 0:
            st.warning("No Tasks Found")

        for task in tasks:

            st.subheader(task["title"])

            st.write("Description:", task["description"])
            st.write("Completed:", task["is_completed"])
            st.write("Task ID:", task["id"])

            st.divider()

    else:
        st.error(response.json())


# ---------------- VIEW ONE TASK ----------------

def view_one_task():

    st.header("View One Task")

    task_id = st.number_input("Enter Task ID", step=1)

    if st.button("Get Task"):

        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        response = requests.get(
            f"{BASE_URL}/tasks/one_task/{task_id}",
            headers=headers
        )

        if response.status_code == 200:

            task = response.json()

            st.subheader(task["title"])
            st.write(task["description"])
            st.write("Completed:", task["is_completed"])

        else:
            st.error(response.json()["detail"])


#-----------------UPDATE TASK -----------------

def update_task():

    st.header("Update Task")

    task_id = st.number_input(
        "Enter Task ID",
        step=1
    )

    title = st.text_input("New Title")
    description = st.text_area("New Description")

    is_completed = st.checkbox("Completed")

    if st.button("Update Task"):

        payload = {
            "title": title,
            "description": description,
            "is_completed": is_completed
        }

        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        response = requests.put(
            f"{BASE_URL}/tasks/update_task/{task_id}",
            json=payload,
            headers=headers
        )

        if response.status_code == 201:

            st.success("Task Updated Successfully")
            st.write(response.json())

        else:
            st.error(response.json()["detail"])

# ---------------- DELETE TASK ----------------

def delete_task():

    st.header("Delete Task")

    task_id = st.number_input("Enter Task ID", step=1)

    if st.button("Delete Task"):

        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        response = requests.delete(
            f"{BASE_URL}/tasks/delete_task/{task_id}",
            headers=headers
        )

        if response.status_code == 204:
            st.success("Task Deleted Successfully")

        else:
            st.error(response.json()["detail"])


# ---------------- DASHBOARD ----------------

def dashboard():

    st.sidebar.title("Dashboard")

    option = st.sidebar.radio(
        "Choose Option",
        [
            "Add Task",
            "View Tasks",
            "View One Task",
            "Update Task",
            "Delete Task"
        ]
    )

    if option == "Add Task":
        add_task()

    elif option == "View Tasks":
        view_tasks()

    elif option == "View One Task":
        view_one_task()

    elif option == "Update Task":
        update_task()

    elif option == "Delete Task":
        delete_task()

    st.sidebar.divider()

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.token = None

        st.rerun()


# ---------------- MAIN ----------------

if st.session_state.logged_in:

    dashboard()

else:

    menu = st.sidebar.selectbox(
        "Menu",
        ["Login", "Register"]
    )

    if menu == "Login":
        login_page()

    else:
        register_page()