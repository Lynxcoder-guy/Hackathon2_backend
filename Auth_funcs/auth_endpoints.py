import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from Auth_funcs.crud_auth import (
    admin_exists,
    check_admin_login,
    check_login,
    check_user_exists,
    check_user_simple,
    regis_admin,
    regis_user,
)
from Auth_funcs.database import get_db

class AdminDatas(BaseModel):
    user_name: str
    user_password: str
    user_email: str
    user_group: str


class LoginData(BaseModel):
    user_name: str
    user_password: str


class SimpleLoginData(BaseModel):
    user_name: str
    user_group: str


class AdminRegisterData(BaseModel):
    user_name: str
    user_password: str
    user_email: str
    user_group: str


router = APIRouter()

#For the admins to sign their users into the system
@router.post("/register-admin", status_code=status.HTTP_201_CREATED)
def register_user(user: AdminDatas, session: Session = Depends(get_db)):
    if check_user_exists(session, user.user_name, user.user_email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists.",
        )
    
    user_token = secrets.token_hex(16)
    regis_user(
        session,
        user.user_name,
        user.user_password,
        user.user_email,
        user_token,
        user.user_group,
    )
    return {"message": "User registered successfully.", "user_token": user_token}

#For admin to check the user data
@router.post("/check-user")
def login_user(user: LoginData, session: Session = Depends(get_db)):
    if not check_login(session, user.user_name, user.user_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )
    return {"message": "Log-in to users account successfully."}


#For easier and simpler login
@router.post("/simple-login")
def simple_login_user(user: SimpleLoginData, session: Session = Depends(get_db)):
    if not check_user_simple(session, user.user_name, user.user_group):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )
    return {"message": "User logged in successfully."}

#For the admin to sign into their console to manage and signed the users
@router.post("/admin-register")
def admin_registration(admin: AdminRegisterData, session: Session = Depends(get_db)):
    if admin_exists(session, admin.user_name, admin.user_email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Admin username or email already exists.",
        )
    
    admin_token = secrets.token_hex(16)
    regis_admin(
        session,
        admin.user_name,
        admin.user_group,
        admin_token,
        admin.user_email,
        admin.user_password
    )
    return {"message": "Admin registered successfully.", "admin_token": admin_token}

#For the admin to log into their console to manage and sign the users
@router.post("/admin-login")
def admin_login(admin: LoginData, session: Session = Depends(get_db)):
    if not check_admin_login(session, admin.user_name, admin.user_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect admin username or password.",
        )
    return {"message": "Admin logged in successfully."}

