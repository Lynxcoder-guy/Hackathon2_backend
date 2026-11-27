import hashlib
import hmac
import secrets
from typing import Optional

from sqlalchemy import Column, String
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()
PASSWORD_HASH_PREFIX = "scrypt$"


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    password_hash = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1
    )
    return f"{PASSWORD_HASH_PREFIX}{salt.hex()}${password_hash.hex()}"


def verify_password(password: str, stored_password: str) -> bool:
    if not stored_password.startswith(PASSWORD_HASH_PREFIX):
        return hmac.compare_digest(password, stored_password)

    try:
        _, salt_hex, hash_hex = stored_password.split("$")
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
    except ValueError:
        return False

    password_hash = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1
    )
    return hmac.compare_digest(password_hash, expected_hash)


class users_auths(Base):
    __tablename__ = "users_auths"
    userName = Column(String(100), primary_key=True, unique=True)
    userPassword = Column(String(255), nullable=False, unique=False)
    email = Column(String(255), nullable=False, unique=True)
    userToken = Column(String(255), nullable=False, unique=True)
    assignedGroup = Column(String(100), nullable=True)

class simple_auth(Base):
    __tablename__ = "simple_auths"
    userName = Column(String(100), primary_key=True, unique=True)  
    userToken = Column(String(255), nullable=False, unique=True)
    userGroup = Column(String(100), nullable=False, unique=False)  # New column for user group


class AdminAuth(Base):
    __tablename__ = "admin_auths"

    adminName = Column(String(100), primary_key=True)
    adminPassword = Column(String(255), nullable=False)
    adminEmail = Column(String(255), nullable=False, unique=True)
    adminToken = Column(String(255), nullable=False, unique=True)
    adminGroupName = Column(String(100), nullable=False)


def regis_user(
    session: Session,
    user_name,
    user_password,
    user_email,
    generated_tokens,
    assign_group: Optional[str] = None,
):
    new_user = users_auths(
        userName=user_name,
        userPassword=hash_password(user_password),
        email=user_email,
        userToken=generated_tokens,
        assignedGroup=assign_group
    )
    session.add(new_user)
    session.commit()
    return {"message": "User registered successfully.", "user_token": generated_tokens}


def check_user_exists(session: Session, user_name, user_email):
    user = (
        session.query(users_auths)
        .filter(
            (users_auths.userName == user_name)
            | (users_auths.email == user_email)
        )
        .first()
    )
    return user is not None

def get_user_password(session: Session, user_token: str) -> Optional[str]:
    user = session.query(users_auths).filter_by(userToken=user_token).first()
    return user.userPassword if user is not None else False


def check_user_password(
    session: Session,
    user_token: str,
    password: str,
) -> bool:
    stored_password = get_user_password(session, user_token)
    if stored_password is False:
        return False
    return verify_password(password, stored_password)


def check_login(session: Session, user_email, user_password):
    user = session.query(users_auths).filter_by(email=user_email).first()
    if user is None or not verify_password(user_password, user.userPassword):
        return False

    if not user.userPassword.startswith(PASSWORD_HASH_PREFIX):
        user.userPassword = hash_password(user_password)
        session.commit()
    return True

def fetched_user_name(session: Session, user_token):
    user = session.query(users_auths).filter_by(userToken=user_token).first()
    return user.userName if user is not None else None

def check_user_simple(session: Session, user_name, user_group):
    user = (
        session.query(simple_auth)
        .filter_by(userName=user_name, userGroup=user_group)
        .first()
    )
    return user is not None


def get_user_token_by_name_and_group(
    session: Session,
    user_name: str,
    user_group: str,
) -> Optional[str]:
    user = (
        session.query(users_auths)
        .filter_by(userName=user_name, assignedGroup=user_group)
        .first()
    )
    return user.userToken if user is not None else None


def regis_admin(session: Session, admin_name, admin_group, generated_tokens, admin_email, admin_password):
    new_user = AdminAuth(
        adminName=admin_name,
        adminToken=generated_tokens,
        adminGroupName=admin_group,
        adminEmail=admin_email,
        adminPassword=hash_password(admin_password),
    )
    session.add(new_user)
    session.commit()
    return {"message": "Admin registered successfully.", "admin_token": generated_tokens}

def admin_exists(session: Session, admin_name, admin_email):
    admin = (
        session.query(AdminAuth)
        .filter(
            (AdminAuth.adminName == admin_name)
            | (AdminAuth.adminEmail == admin_email)
        )
        .first()
    )
    return admin is not None

def delete_user_by_token(session: Session, user_token):
    deletion = (session.query(users_auths).filter(users_auths.userToken == user_token).first())
    if deletion:
        session.delete(deletion)
        session.commit()
        return True
    else:
        return False

def admin_name(session: Session, admin_token: str):
    admin = session.query(AdminAuth).filter_by(adminToken=admin_token).first()
    return admin.adminName if admin is not None else False


def authenticate_admin(
    session: Session,
    admin_email: str,
    admin_password: str,
) -> Optional[str]:
    return get_admin_token(session, admin_email, admin_password)

def get_admin_token(
    session: Session,
    admin_email: str,
    admin_password: str,
) -> Optional[str]:
    admin = session.query(AdminAuth).filter_by(adminEmail=admin_email).first()
    if admin is None or not verify_password(admin_password, admin.adminPassword):
        return None

    if not admin.adminPassword.startswith(PASSWORD_HASH_PREFIX):
        admin.adminPassword = hash_password(admin_password)
        session.commit()
    return admin.adminToken


def check_admin_login(session: Session, admin_email, admin_password) -> bool:
    return authenticate_admin(session, admin_email, admin_password) is not None

def get_all_managed_users(
    session: Session,
    admin_token: str,
) -> Optional[list[dict[str, Optional[str]]]]:
    admin = session.query(AdminAuth).filter_by(adminToken=admin_token).first()
    if admin is None:
        return None

    users = (
        session.query(users_auths)
        .filter_by(assignedGroup=admin.adminGroupName)
        .order_by(users_auths.userName)
        .all()
    )
    return [
        {
            "user_name": user.userName,
            "user_token": user.userToken,
        }
        for user in users
    ]


def get_group_name(session: Session, admin_token: str) -> Optional[str]:
    admin = session.query(AdminAuth).filter_by(adminToken=admin_token).first()
    return admin.adminGroupName if admin is not None else None


def get_managed_user_number(session: Session, group_name: str) -> int:
    return (
        session.query(users_auths)
        .filter_by(assignedGroup=group_name)
        .count()
    )



#========================================================
# The functions below are for terminal testing purposes.
#========================================================
def delete_user(session: Session, user_name, user_email):
    user = (
        session.query(users_auths)
        .filter_by(userName=user_name, email=user_email)
        .first()
    )
    if user:
        session.delete(user)
        session.commit()


def update_user(session: Session, user_name, user_email, new_password):
    user = (
        session.query(users_auths)
        .filter_by(userName=user_name, email=user_email)
        .first()
    )
    if user:
        user.userPassword = hash_password(new_password)
        session.commit()


def view_user(session: Session, user_name, user_email):
    return (
        session.query(users_auths)
        .filter_by(userName=user_name, email=user_email)
        .first()
    )
 
def view_all(session: Session):
    return session.query(users_auths).all()

def exit():
    print("Exiting terminal tester.")
    raise SystemExit