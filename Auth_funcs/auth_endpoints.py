import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from Auth_funcs.crud_auth import (
    admin_exists,
    check_admin_login,
    check_login,
    check_user_exists,
    get_all_managed_users as fetch_all_managed_users,
    get_group_name,
    get_managed_user_number,
    get_user_token_by_name_and_group,
    check_user_password,
    regis_admin,
    regis_user,
    fetched_user_name,
    admin_name,
    get_admin_token,
    delete_user_by_token as delete_user_record,
)
from Auth_funcs.database import get_db

class UserDatas(BaseModel):
    user_name: str
    user_password: str
    user_email: str
    user_group: str


class LoginData(BaseModel):
    user_email: str
    user_password: str


class UserPasswordVerification(BaseModel):
    user_token: str
    user_password: str


class UserTokenRequest(BaseModel):
    user_token: str


class DeleteUserRequest(BaseModel):
    admin_token: str
    user_token: str
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
@router.post("/register-user")
def register_user(user: UserDatas, session: Session = Depends(get_db)) -> bool:
    if check_user_exists(session, user.user_name, user.user_email):
        return False
    
    user_token = secrets.token_hex(16)
    regis_user(
        session,
        user_name=user.user_name,
        user_password=user.user_password,
        user_email=user.user_email,
        generated_tokens=user_token,
        assign_group=user.user_group,
    )
    return True

#For admin to check the user data
@router.post("/check-user")
def login_user(user: LoginData, session: Session = Depends(get_db)):
    if not check_login(session, user.user_email, user.user_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )
    return {"message": "Log-in to users account successfully."}


#For easier and simpler login
@router.post("/simple-login")
def simple_login_user(user: SimpleLoginData, session: Session = Depends(get_db)):
    user_token = get_user_token_by_name_and_group(
        session,
        user.user_name,
        user.user_group,
    )
    if user_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )
    return {
        "message": "User logged in successfully.",
        "user_token": user_token,
    }


@router.post("/get-username")
def get_user_name(
    request: UserTokenRequest,
    session: Session = Depends(get_db),
):
    user_name = fetched_user_name(session, request.user_token)
    if user_name is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user_name

@router.post("/delete-user")
def delete_managed_user(
    request: DeleteUserRequest,
    session: Session = Depends(get_db),
):
    managed_users = fetch_all_managed_users(session, request.admin_token)
    if managed_users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found.",
        )

    if not any(user["user_token"] == request.user_token for user in managed_users):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Managed user not found.",
        )

    if not check_user_password(
        session,
        request.user_token,
        request.user_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user password.",
        )

    if not delete_user_record(session, request.user_token):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return {"success": True, "message": "User deleted successfully."}



@router.post("/admin-name/{adminToken}")
def get_admin_name(adminToken: str, session: Session = Depends(get_db)):
    fetched_admin_name = admin_name(session, adminToken)
    if fetched_admin_name is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found.",
        )
    return fetched_admin_name

#For the admin to sign into their console to manage and signed the users
@router.post("/register-admin")
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

@router.get("/console-additional-data")
def get_additional_data(user_token: str, session: Session = Depends(get_db)):
    group_name = get_group_name(session, user_token)
    if group_name is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found.",
        )
    managed_user_number = get_managed_user_number(session, group_name)
    return {"group_name": group_name, "managed_users": managed_user_number}

#For the admin to log into their console to manage and sign the users
@router.post("/admin-login")
def admin_login(admin: LoginData, session: Session = Depends(get_db)):
    if not check_admin_login(session, admin.user_email, admin.user_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect admin email or password.",
        )
    return {"message": True}


@router.post("/admin-token")
def get_admin_token_endpoint(admin: LoginData, session: Session = Depends(get_db)):
    admin_token = get_admin_token(
        session,
        admin.user_email,
        admin.user_password,
    )
    if admin_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect admin email or password.",
        )
    return admin_token

@router.get("/get-managed-users/{user_token}")
def get_all_managed_users(
    user_token: str,
    session: Session = Depends(get_db),
):
    listed_users = fetch_all_managed_users(session, user_token)
    if listed_users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found.",
        )
    return listed_users

@router.post("/verify-user-password", response_model=bool)
def verify_user_password(
    request: UserPasswordVerification,
    session: Session = Depends(get_db),
) -> bool:
    return check_user_password(
        session,
        request.user_token,
        request.user_password,
    )

