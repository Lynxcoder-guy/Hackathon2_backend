from sqlalchemy.orm import Session

from Auth_funcs.crud_auth import users_auths, verify_password
from Weekly_Condition_logs.wcl_crud import user_weekly_logs


def get_health_logs(db: Session, userToken: str):
    logs = (
        db.query(user_weekly_logs.healthLogs, user_weekly_logs.createdWhen)
        .filter(user_weekly_logs.userToken == userToken)
        .order_by(user_weekly_logs.createdWhen.asc())
        .all()
    )
    return [
        {"healthLogs": row.healthLogs, "createdWhen": row.createdWhen}
        for row in logs
    ]


def get_user_name(db: Session, userToken: str):
    user = (
        db.query(users_auths)
        .filter(users_auths.userToken == userToken)
        .first()
    )
    return user.userName if user else False

def get_user_group(db: Session, user_token: str):
    user = (
        db.query(users_auths)
        .filter(users_auths.userToken == user_token)
        .first()
    )
    return user.assignedGroup if user else False


def validate_checkup(
    db: Session,
    user_name: str,
    user_group: str,
    user_password: str,
) -> bool:
    user = (
        db.query(users_auths)
        .filter(
            users_auths.userName == user_name,
            users_auths.assignedGroup == user_group,
        )
        .first()
    )
    if user is None:
        return False

    return verify_password(user_password, user.userPassword)
