import json
import getpass
import secrets
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from Auth_funcs.database import createTableInCase
from Auth_funcs.crud_auth import (
    AdminAuth,
    PASSWORD_HASH_PREFIX,
    admin_exists,
    check_login,
    check_user_exists,
    check_user_simple,
    delete_user,
    get_admin_token,
    get_user_password,
    regis_admin,
    regis_user,
    simple_auth,
    update_user,
    users_auths,
)
from Pre_Checkup.gobbie.gobbie_ai.precheckup_ai import PreCheckupAI
from Pre_Checkup.pre_checkup_crud import get_health_logs, get_user_name


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
    
    assign_group = input("User group: ").strip()
    password = getpass.getpass("Password: ")
    regis_user(session, user_name, password, user_email, secrets.token_hex(16), assign_group)
    print("User registered; password saved as a hash.")


def _login_user(session: Session):
    user_name = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    if check_login(session, user_name, password):
        print("Login successful.")
    else:
        print("Login failed.")


def _test_get_user_password(session: Session):
    user_token = input("User token: ").strip()
    password = get_user_password(session, user_token)
    if password is None:
        print("User not found.")
        return

    password_status = (
        "hashed"
        if password.startswith(PASSWORD_HASH_PREFIX)
        else "plain text (legacy)"
    )
    print(f"Password found; stored as {password_status}.")


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
    admin_email = input("Admin email: ").strip()
    password = getpass.getpass("Admin password: ")
    admin_token = get_admin_token(session, admin_email, password)
    if admin_token is None:
        print("Admin login failed.")
        return

    print("Admin login successful.")
    print(f"Admin token: {admin_token}")


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


def _create_missing_tables(_: Session):
    createTableInCase()
    print("Database tables are ready.")


def _test_pre_checkup_summary(session: Session):
    user_token = getpass.getpass("User token (input hidden): ").strip()
    if not user_token:
        print("User token is required.")
        return

    logs = get_health_logs(session, user_token)
    if not logs:
        print("No health logs found for this user.")
        return

    confirmation = input(
        f"Send {len(logs)} health log(s) to Gemini for a summary? (y/N): "
    ).strip().lower()
    if confirmation != "y":
        print("Pre-checkup summary test cancelled.")
        return

    try:
        ai = PreCheckupAI()
    except ValueError as error:
        print(f"Pre-checkup AI is not configured: {error}")
        return

    patient_data = {
        "patient_id": "anonymous",
        "logs": json.loads(json.dumps(logs, separators=(",", ":"), default=str)),
    }
    summary = ai.generate_summary(patient_data)
    summary["generated_at"] = datetime.now(timezone.utc).isoformat()

    print("Pre-checkup AI summary:")
    print(
        json.dumps(
            {"Name": get_user_name(session, user_token), "Summary": summary},
            ensure_ascii=False,
            indent=2,
        )
    )


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
        "14": ("Create missing tables if needed", _create_missing_tables),
        "15": ("Test get user password by token", _test_get_user_password),
        "16": ("Test pre-checkup summary with Gobbie AI", _test_pre_checkup_summary),
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
