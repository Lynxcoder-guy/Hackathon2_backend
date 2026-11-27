from sqlalchemy.orm import Session
import secrets
from Auth_funcs.crud_auth import (
    check_user_exists,
    delete_user,
    regis_user,
    update_user,
    view_user,
    view_all,
    exit, 
)


def terminal_db_tester(session: Session):
    act = input("Enter the action you want to perform (add, delete, update, view, view_all, exit): ")
    if act == "add":
        user_name = input("Enter user name: ")
        user_password = input("Enter user password: ")
        user_email = input("Enter user email: ")
        generated_tokens = secrets.token_hex(16)
        regis_user(session, user_name, user_password, user_email, generated_tokens)
        print("User added successfully.")
    elif act == "delete":
        user_name = input("Enter user name to delete: ")
        user_email = input("Enter user email to delete: ")
        # Implement delete_user function in crud_auth.py
        delete_user(session, user_name, user_email)
        print("User deleted successfully.")
    elif act == "update":
        user_name = input("Enter user name to update: ")
        user_email = input("Enter user email to update: ")
        new_password = input("Enter new password: ")
        # Implement update_user function in crud_auth.py
        update_user(session, user_name, user_email, new_password)
        print("User updated successfully.")
    elif act == "view":
        user_name = input("Enter user name to view: ")
        user_email = input("Enter user email to view: ")
        # Implement view_user function in crud_auth.py
        user = view_user(session, user_name, user_email)
        if user:
            print(f"User Name: {user.userName}, Email: {user.email}")
        else:
            print("User not found.")
    elif act == "view_all":
        # Implement view_all_users function in crud_auth.py
        users = view_all(session)
        if users:
            for user in users:
                print(f"User Name: {user.userName}, Email: {user.email}")
        else:
            print("No users found.")
    elif act == "exit":
        print("Exiting terminal tester.")