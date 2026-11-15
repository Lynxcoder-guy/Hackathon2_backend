import getpass
import secrets

from sqlalchemy.orm import Session

from Auth_funcs.crud_auth import (
    AdminAuth,
    PASSWORD_HASH_PREFIX,
    admin_exists,
    check_admin_login,
    check_login,
    check_user_exists,
    check_user_simple,
    delete_user,
    regis_admin,
    regis_user,
    simple_auth,
    update_user,
    users_auths,
)


def _show_users(session: Session):
    users = session.query(users_auths).order_by(users_auths.userName).all()
    if not users:
        print("No registered users.")
        return

    for user in users:
        password_status = (
            "hashed"
            if user.userPassword.startswith(PASSWORD_HASH_PREFIX)
            else "plain text (legacy)"
        )
        print(f"{user.userName} | {user.email} | password: {password_status}")


def _show_admins(session: Session):
    admins = session.query(AdminAuth).order_by(AdminAuth.adminName).all()
    if not admins:
        print("No registered admins.")
        return

    for admin in admins:
        password_status = (
            "hashed"
            if admin.adminPassword.startswith(PASSWORD_HASH_PREFIX)
            else "plain text (legacy)"
        )
        print(
            f"{admin.adminName} | {admin.adminEmail} | "
            f"group: {admin.adminGroupName} | password: {password_status}"
        )


def _show_simple_users(session: Session):
    users = session.query(simple_auth).order_by(simple_auth.userName).all()
    if not users:
        print("No simple-login users.")
        return

    for user in users:
        print(f"{user.userName} | group: {user.userGroup}")


def _register_user(session: Session):
    user_name = input("Username: ").strip()
    user_email = input("Email: ").strip()
    if check_user_exists(session, user_name, user_email):
        print("That username or email is already registered.")
        return

    password = getpass.getpass("Password: ")
    regis_user(session, user_name, password, user_email, secrets.token_hex(16))
    print("User registered; password saved as a hash.")


def _login_user(session: Session):
    user_name = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    if check_login(session, user_name, password):
        print("Login successful.")
    else:
        print("Login failed.")


def _update_user_password(session: Session):
    user_name = input("Username: ").strip()
    user_email = input("Email: ").strip()
    user = (
        session.query(users_auths)
        .filter_by(userName=user_name, email=user_email)
        .first()
    )
    if user is None:
        print("User not found.")
        return

    update_user(session, user_name, user_email, getpass.getpass("New password: "))
    print("Password updated and saved as a hash.")


def _delete_user(session: Session):
    user_name = input("Username: ").strip()
    user_email = input("Email: ").strip()
    user = (
        session.query(users_auths)
        .filter_by(userName=user_name, email=user_email)
        .first()
    )
    if user is None:
        print("User not found.")
        return

    delete_user(session, user_name, user_email)
    print("User deleted.")


def _register_admin(session: Session):
    admin_name = input("Admin username: ").strip()
    admin_email = input("Admin email: ").strip()
    if admin_exists(session, admin_name, admin_email):
        print("That admin username or email is already registered.")
        return

    admin_group = input("Admin group: ").strip()
    password = getpass.getpass("Admin password: ")
    regis_admin(
        session,
        admin_name,
        admin_group,
        secrets.token_hex(16),
        admin_email,
        password,
    )
    print("Admin registered; password saved as a hash.")


def _login_admin(session: Session):
    admin_name = input("Admin username: ").strip()
    password = getpass.getpass("Admin password: ")
    if check_admin_login(session, admin_name, password):
        print("Admin login successful.")
    else:
        print("Admin login failed.")


def _add_simple_user(session: Session):
    user_name = input("Username: ").strip()
    user_group = input("User group: ").strip()
    if session.query(simple_auth).filter_by(userName=user_name).first():
        print("That username already exists.")
        return

    session.add(
        simple_auth(
            userName=user_name,
            userGroup=user_group,
            userToken=secrets.token_hex(16),
        )
    )
    session.commit()
    print("Simple-login user added. This table does not store a password.")


def _test_simple_login(session: Session):
    user_name = input("Username: ").strip()
    user_group = input("User group: ").strip()
    if check_user_simple(session, user_name, user_group):
        print("Simple login successful.")
    else:
        print("Simple login failed.")


def _delete_admin(session: Session):
    admin_name = input("Admin username: ").strip()
    admin_email = input("Admin email: ").strip()
    admin = (
        session.query(AdminAuth)
        .filter_by(adminName=admin_name, adminEmail=admin_email)
        .first()
    )
    if admin is None:
        print("Admin not found.")
        return

    session.delete(admin)
    session.commit()
    print("Admin deleted.")


def _delete_simple_user(session: Session):
    user_name = input("Username: ").strip()
    user_group = input("User group: ").strip()
    user = (
        session.query(simple_auth)
        .filter_by(userName=user_name, userGroup=user_group)
        .first()
    )
    if user is None:
        print("Simple-login user not found.")
        return

    session.delete(user)
    session.commit()
    print("Simple-login user deleted.")


def terminal_db_tester(session: Session):
    actions = {
        "1": ("Register user", _register_user),
        "2": ("Test user login", _login_user),
        "3": ("List users and password storage", _show_users),
        "4": ("Change user password", _update_user_password),
        "5": ("Delete user", _delete_user),
        "6": ("Register admin", _register_admin),
        "7": ("Test admin login", _login_admin),
        "8": ("List admins and password storage", _show_admins),
        "9": ("Add simple-login user", _add_simple_user),
        "10": ("Test simple login", _test_simple_login),
        "11": ("List simple-login users", _show_simple_users),
        "12": ("Delete simple-login user", _delete_simple_user),
        "13": ("Delete admin", _delete_admin),
    }

    while True:
        print("\nDatabase tester")
        for key, (label, _) in actions.items():
            print(f"{key}. {label}")
        print("0. Back")

        choice = input("Choose an option: ").strip()
        if choice == "0":
            return

        action = actions.get(choice)
        if action is None:
            print("Choose one of the listed options.")
            continue
        action[1](session)
